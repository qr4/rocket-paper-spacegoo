import socket, json
import random, pprint

# import view
# view.init(1024, 768)

USERNAME = "nopper"
PASSWORD = "bar"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 6000))
io = s.makefile('rw')

def write(data):
    io.write('%s\n' % (data,))
    io.flush()

write('login %s %s' % (USERNAME, PASSWORD))
while 1:
    data = io.readline().strip()
    if not data:
        break
    if data and data[0] == "{":
        write("nop")
    else:
        print data
