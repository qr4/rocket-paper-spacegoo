import socket, json

USERNAME = "foo"
PASSWORD = "bar"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.142', 6000))
io = s.makefile('rw')

def write(data):
    io.write('%s\n' % (data,))
    io.flush()

write('login %s %s' % (USERNAME, PASSWORD))
while 1:
    data = io.readline()
    if data[0] == "{":
        state = json.loads(data)
        print state
