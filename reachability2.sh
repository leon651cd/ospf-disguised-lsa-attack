#!/bin/bash

lxterminal -e "/bin/bash -c 'echo \"origin h2-1 destination h1-1\"; ./curl.sh h2-1 h1-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h2-1 destination h3-1\"; ./curl.sh h2-1 h3-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h2-1 destination h4-1\"; ./curl.sh h2-1 h4-1'" &
lxterminal -e "/bin/bash -c 'echo \"origin h2-1 destination h5-1\"; ./curl.sh h2-1 h5-1'" &
