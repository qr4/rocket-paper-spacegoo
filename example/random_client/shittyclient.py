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
        break
    elif data[0] == "{":
        state = json.loads(data)
        # pprint.pprint(state)

        if state['winner'] is not None or state['game_over']:
            print("final: %s" % state['winner'])
            break

        player_id = state['player_id']

        enemy_planets = [planet for planet in state['planets'] if planet['owner_id'] != player_id]
        my_planets = [planet for planet in state['planets'] if planet['owner_id'] == player_id]

        # which planets I can go to
        hyperlanes_map = {}
        for lane in state['hyperlanes']:
            if lane[0] not in hyperlanes_map:
                hyperlanes_map[lane[0]] = []

            hyperlanes_map[lane[0]].append(lane[1])

        # map planet_id -> planet
        planets_map = {planet['id'] : planet for planet in state['planets']}

        if not my_planets:
            write("nop")
        elif not enemy_planets:
            write("nop")
        else:
            source_planet = random.choice(my_planets)
            target_planet_id = random.choice(hyperlanes_map[source_planet['id']])
            target_planet = planets_map[target_planet_id]

            # reachable enemy planets
            write("send %s %s %d %d %d" % (
                source_planet['id'],
                target_planet['id'],
                source_planet['ships'][0]/6,
                source_planet['ships'][1]/6,
                source_planet['ships'][2]/6))
    else:
        print(data)
