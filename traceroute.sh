#!/bin/bash

snode=$1
dnode=$2

sudo python run.py --snode $snode --dnode $dnode --cmd "sudo traceroute6"
