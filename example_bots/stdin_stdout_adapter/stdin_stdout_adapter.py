#!/usr/bin/env python3
import socket
import json
import sys

# this client takes care of the tcp stuff and passes data to stdout, reads from stdin and passes it
# back to the server

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('rps.vhenne.de', 6000))
io = s.makefile('rw')

def write(data):
    io.write('%s\n' % (data,))
    io.flush()


write('login %s %s' % (USERNAME, PASSWORD))

while 1:
    data = io.readline().strip()
    if not data:
        break
    elif data[0] == "{":
        state = json.loads(data)
        if state['winner'] is not None or state['game_over']:
            break

        # feel free to preprocess the data before passing it to your actual client...
        print(data, flush=True)

        cmd = sys.stdin.readline().strip()

        print("will send: " + cmd, file=sys.stderr, flush=True)
        write(cmd)
