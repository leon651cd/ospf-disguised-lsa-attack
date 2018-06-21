#!/usr/bin/env python

import sys
import os
import termcolor as T
import time
import datetime

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel
from mininet.util import dumpNodeConnections, quietRun, moveIntf, waitListening
from mininet.cli import CLI
from mininet.node import Switch, OVSSwitch, Controller, RemoteController
from subprocess import Popen, PIPE, check_output
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

ROUTERS = 12
OSPF_CONVERGENCE_TIME = 30
CAPTURING_WINDOW = 120

SWITCH_NAME = 'switch'
ATTACKER_NAME = 'atk1'

setLogLevel('info')
#setLogLevel('debug')

parser = ArgumentParser("Configure simple OSPF network in Mininet.")
parser.add_argument('--sleep', default=3, type=int)
args = parser.parse_args()


def log(s, col="green"):
	print T.colored(s, col)


class Router(Switch):
	"""
	Defines a new router that is inside a network namespace so that the
	individual routing entries don't collide.
	"""
	ID = 0
	def __init__(self, name, **kwargs):
		kwargs['inNamespace'] = True
		Switch.__init__(self, name, **kwargs)
		Router.ID += 1
		self.switch_id = Router.ID

	@staticmethod
	def setup():
		return

	def start(self, controllers):
		pass

	def stop(self):
		self.deleteIntfs()

	def log(self, s, col="magenta"):
		print T.colored(s, col)


class SimpleTopo(Topo):

	def __init__(self):
		# Add default members to class.
		super(SimpleTopo, self ).__init__()

		num_routers = ROUTERS

		routers = []
		for i in xrange(num_routers):
			router = self.addSwitch('R%d' % (i+1))
			routers.append(router)

		hosts = []
		for i in xrange(5):
			host = self.addNode('h%d-1' % (i+1))
			hosts.append(host)
		
		# adding links between routers
		self.addLink('R1', 'R10')
		self.addLink('R10', 'R11')
		self.addLink('R11', 'R6')
		self.addLink('R10', 'R12')
		self.addLink('R12', 'R6')
		self.addLink('R12', 'R2')
		self.addLink('R6', 'R7')
		self.addLink('R6', 'R8')
		self.addLink('R7', 'R4')
		self.addLink('R4', 'R8')
		self.addLink('R4', 'R3')
		self.addLink('R8', 'R9')
		self.addLink('R9', 'R5')
		
		for i in xrange(5):
			switch_name = SWITCH_NAME + str(i+1)
			self.addSwitch(switch_name, cls=OVSSwitch)
			self.addLink(switch_name, 'R%d' % (i+1))
			self.addLink(switch_name, 'h%d-1' % (i+1))
		
		return


def getIP(hostname):
	if hostname == ATTACKER_NAME:
		return '10.0.4.66/24'

	subnet, idx = hostname.replace('h', '').split('-')

	ip = '10.0.%s.%s/24' % (subnet, idx)

	return ip


def getGateway(hostname):
	if hostname == ATTACKER_NAME:
		return '10.0.4.254'

	subnet, idx = hostname.replace('h', '').split('-')

	gw = '10.0.%s.254' % (subnet)

	return gw


def startWebserver(net, hostname, text="Default web server"):
	host = net.getNodeByName(hostname)
	return host.popen("python webserver.py --text '%s'" % text, shell=True)


def launch_attack(attacker_host):
	log("launching attack", 'red')

	attacker_host.popen("python attacker_attack.py > /tmp/%s_attacker_attack.log 2>&1" % ATTACKER_NAME, shell=True)
	os.system('lxterminal -e "/bin/bash -c \'tail -f /tmp/%s_attacker_attack.log\'" > /dev/null 2>&1 &' % ATTACKER_NAME)

	log("attack launched", 'red')


def main():
	os.system("rm -f /tmp/R*.log /tmp/ospf-R?.pid /tmp/zebra-R?.pid 2> /dev/null")
	os.system("rm -r logs/*stdout /tmp/h*tcpdump.cap 2> /dev/null")
	os.system("rm -r /tmp/R?_tcpdump.cap /tmp/R?_tcpdump.log 2> /dev/null")
	os.system("mn -c > /dev/null 2>&1")
	os.system("killall -9 zebra ospfd > /dev/null 2>&1")
	os.system('pgrep -f webserver.py | xargs kill -9')

	net = Mininet(topo=SimpleTopo(), switch=Router)
	net.start()

	attacker_host = None

	# CONFIGURING HOSTS
	for host in net.hosts:
		host.cmd("ifconfig %s-eth0 %s" % (host.name, getIP(host.name)))
		host.cmd("route add default gw %s" % (getGateway(host.name)))

		host.cmd("tcpdump -i %s-eth0 -w /tmp/%s_tcpdump.cap &" % (host.name, host.name))

		if host.name == ATTACKER_NAME:
			attacker_host = host
			continue
		else:
			log("Starting web server on %s" % host.name, 'yellow')
			startWebserver(net, host.name, "Web server on %s" % host.name)

	# CONFIGURING ROUTERS
	for router in net.switches:
		if SWITCH_NAME not in router.name:
			router.cmd("sysctl -w net.ipv4.ip_forward=1")
			router.waitOutput()

	log("Waiting %d seconds for sysctl changes to take effect..." % args.sleep, col='cyan')
	sleep(args.sleep)

	for router in net.switches:
		if SWITCH_NAME not in router.name:
			router.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (router.name, router.name, router.name))
			router.waitOutput()
			router.cmd("/usr/lib/quagga/ospfd -f conf/ospfd-%s.conf -d -i /tmp/ospf-%s.pid > logs/%s-ospfd-stdout 2>&1" % (router.name, router.name, router.name), shell=True)
			router.waitOutput()
			log("Starting zebra and ospfd on %s" % router.name)

			router.cmd("tcpdump -i any -w /tmp/%s_tcpdump.cap 2>&1 > /tmp/%s_tcpdump.log &" % (router.name, router.name))
	
	#"""
	log("Waiting for OSPF convergence (estimated %s)..." % \
		((datetime.datetime.now()+datetime.timedelta(0,OSPF_CONVERGENCE_TIME)).strftime("%H:%M:%S")), 'cyan')
	sleep(OSPF_CONVERGENCE_TIME)
	#"""

	#launch_attack(attacker_host)
	
	"""
	log("Collecting data for %s seconds (estimated %s)..." % \
		(CAPTURING_WINDOW, (datetime.datetime.now()+datetime.timedelta(0,CAPTURING_WINDOW)).strftime("%H:%M:%S")), 'cyan')
	sleep(CAPTURING_WINDOW)
	#"""

	#os.system("./ping.sh")
	
	CLI(net)
	net.stop()

	os.system("killall -9 zebra ospfd")
	os.system('pgrep -f webserver.py | xargs kill -9')


if __name__ == "__main__":
	main()
