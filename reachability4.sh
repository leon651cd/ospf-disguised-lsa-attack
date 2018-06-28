#!/bin/bash

lxterminal -e "/bin/bash -c 'echo \"origin h4-1 destination h1-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h4-1 h1-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h4-1 destination h2-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h4-1 h2-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h4-1 destination h3-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h4-1 h3-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h4-1 destination h5-1\"; /home/mininet/ospf-disguised-lsa-attack/curl.sh h4-1 h5-1'" &
