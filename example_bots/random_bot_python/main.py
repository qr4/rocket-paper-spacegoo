#!/usr/bin/env python3
import socket, json
import random, pprint

USERNAME = "<PICK_AN_USER_NAME>"
PASSWORD = "<PICK_A_PASSWORD>"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('rps.qr4.dev', 6000))
io = s.makefile('rw')


# only an asymetric round. this needs to be called twice
def battle_round(attacker,defender):
    numships = len(attacker)
    defender = defender[::]
    for def_type in range(0,numships):
        for att_type in range(0,numships):
            if def_type == att_type:
                multiplier = 0.1
                absolute = 1
            if (def_type-att_type)%numships == 1:
                multiplier = 0.25
                absolute = 2
            if (def_type-att_type)%numships == numships-1:
                multiplier = 0.01
                absolute = 1
            defender[def_type] -= max((attacker[att_type]*multiplier), (attacker[att_type] > 0) * absolute)
        defender[def_type] = max(0,defender[def_type])
    return defender


# simulates a battle of two fleets `s1` and `s2`.
# returns the surviving ships of each fleet after the battle
# Note: One of the fleet will always be eliminated
def battle(s1,s2):
    ships1 = s1[::]
    ships2 = s2[::]
    while sum(ships1) > 0 and sum(ships2) > 0:
        new1 = battle_round(ships2,ships1)
        ships2 = battle_round(ships1,ships2)
        ships1 = new1

    ships1 = list(map(int,ships1))
    ships2 = list(map(int,ships2))
    return ships1, ships2



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
            print("Game Over.")
            break

        player_id = state['player_id']

        # very simple approach: Find planet under our control which has the most ships
        # and send 1/6 of each to a random planet which is _not_ under our control.
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
