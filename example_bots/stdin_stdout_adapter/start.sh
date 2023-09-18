#!/bin/bash
[ "$#" -ne 3 ] && echo "USAGE $0 <YOUR PROGRAM> <user> <password>" && exit

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

socat EXEC:"$DIR/stdin_stdout_adapter.py $2 $3" EXEC:"$1",nofork
