#!/bin/bash

node="h4-1"


sudo python run.py --node $node --cmd "ping -c 1 10.0.1.1"
echo
sudo python run.py --node $node --cmd "ping -c 1 10.0.2.1"
echo
sudo python run.py --node $node --cmd "ping -c 1 10.0.3.1"
echo
sudo python run.py --node $node --cmd "ping -c 1 10.0.5.1"
