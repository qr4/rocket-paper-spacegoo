#!/bin/bash
[ "$#" -ne 1 ] && echo "USAGE $0 <YOUR PROGRAM>" && exit

socat EXEC:./stdin_stdout_adapter.py EXEC:$1,nofork
