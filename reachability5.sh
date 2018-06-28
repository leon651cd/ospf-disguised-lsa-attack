#!/bin/bash

lxterminal -e "/bin/bash -c 'echo \"origin h5-1 destination h1-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h5-1 h1-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h5-1 destination h2-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h5-1 h2-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h5-1 destination h3-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h5-1 h3-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h5-1 destination h4-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h5-1 h4-1'" &
