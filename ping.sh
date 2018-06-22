#!/bin/bash

node="h1-1"

sudo python run.py --node $node --cmd "ping -c 1 10.0.2.1"
sudo python run.py --node $node --cmd "ping -c 1 10.0.3.1"
sudo python run.py --node $node --cmd "ping -c 1 10.0.4.1"
sudo python run.py --node $node --cmd "ping -c 1 10.0.5.1"
