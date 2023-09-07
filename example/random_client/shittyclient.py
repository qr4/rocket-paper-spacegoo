#!/usr/bin/env python3
import socket, json
import random, pprint

USERNAME = "<INSERT NAME HERE>"
PASSWORD = "<INSERT PW HERE>"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 6000))
io = s.makefile('rw')


def write(data):
    io.write('%s\n' % (data,))
    io.flush()
    print("SENDING ", data)


write('login %s %s' % (USERNAME, PASSWORD))

while 1:
    data = io.readline().strip()
    if not data:
        print("waaait")
        continue
        break
    elif data[0] == "{":
        state = json.loads(data)
        # pprint.pprint(state)

        if state['winner'] is not None or state['game_over']:
            print("final: %s" % state['winner'])
            break

        player_id = state['player_id']

        enemy_planets = [planet for planet in state['planets'] if planet['owner_id'] != player_id]
        my_planets = [(sum(planet['ships']), planet) for planet in state['planets'] if planet['owner_id'] == player_id]
        my_planets.sort(key=lambda d: d[0])

        if not my_planets:
            write("nop")
        elif not enemy_planets:
            write("nop")
        else:
            best_planet = my_planets[-1][1]
            target_planet = random.choice(enemy_planets)

            write("send %s %s %d %d %d" % (
                best_planet['id'],
                target_planet['id'],
                best_planet['ships'][0]/6,
                best_planet['ships'][1]/6,
                best_planet['ships'][2]/6))
    else:
        print(data)
