import socket, json
import random, pprint

USERNAME = "dividuum"
PASSWORD = "bar"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.142', 6000))
io = s.makefile('rw')

def write(data):
    io.write('%s\n' % (data,))
    io.flush()

write('login %s %s' % (USERNAME, PASSWORD))
while 1:
    data = io.readline().strip()
    if data[0] == "{":
        state = json.loads(data)
        pprint.pprint(state)
        if state['status'] is not None:
            print "final: %s" % state['status']
            break

        player_id = state['player_id']

        enemy_planets = [planet for planet in state['planets'] if planet['owner_id'] != player_id]
        my_planets = [(sum(planet['ships']), planet) for planet in state['planets'] if planet['owner_id'] == player_id]
        my_planets.sort()

        if not my_planets:
            write("nop")
        elif not enemy_planets:
            write("nop")
        else:
            print len(my_planets)
            best_planet = my_planets[-1][1]
            target_planet = random.choice(enemy_planets)
            
            write("send %s %s %d %d %d" % (
                best_planet['id'], 
                target_planet['id'], 
                best_planet['ships'][0]/2,
                best_planet['ships'][1]/2, 
                best_planet['ships'][2]/2))
    else:
        print data

