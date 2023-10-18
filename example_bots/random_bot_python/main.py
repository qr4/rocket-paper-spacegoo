#!/usr/bin/env python3
import socket, json
import random, pprint

USERNAME = "<PICK_AN_USER_NAME>"
PASSWORD = "<PICK_A_PASSWORD>"

# only an asymetric round. this needs to be called twice
# ship_type_0 > ship_type_1 > ship_type_2 > ship_type_0
def battle_round(attacker,defender):
    numships = len(attacker)
    defender = defender[::] # copy the defenders array
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
    ships1 = s1[::] # copy the ships of player 1
    ships2 = s2[::] # copy the ships of player 2

    # while there are ships remaining, they battle
    while sum(ships1) > 0 and sum(ships2) > 0:
        new1 = battle_round(ships2,ships1)
        ships2 = battle_round(ships1,ships2)
        ships1 = new1

    ships1 = list(map(int,ships1))
    ships2 = list(map(int,ships2))
    return ships1, ships2


def write(io, data):
    io.write('%s\n' % (data,))
    io.flush()
    print("SENDING ", data)


def send_pass_command(io):
    write(io, "nop")

def send_fleet_command(io, source_planet_id, target_planet_id, ships_0, ships_1, ships_2):
    write(io, "send %s %s %d %d %d" % (
        source_planet_id,
        target_planet_id,
        ships_0,
        ships_1,
        ships_2))


# TODO: Improve me!
def compute_move(io, state):
    player_id = state['player_id'] # your player id

    enemy_planets = [planet for planet in state['planets'] if planet['owner_id'] != player_id]
    my_planets = [(sum(planet['ships']), planet) for planet in state['planets'] if planet['owner_id'] == player_id]
    my_planets.sort(key=lambda d: d[0])

    if not my_planets:
        send_pass_command(io)
    elif not enemy_planets:
        send_pass_command(io)
    else:
        # pick a planet you own with the most ships
        best_planet = my_planets[-1][1]

        # pick a random enemy planet
        target_planet = random.choice(enemy_planets)

        # send 1/6 of each ship type
        send_fleet_command(io,
                best_planet["id"],
                target_planet["id"],
                best_planet['ships'][0]/6,
                best_planet['ships'][1]/6,
                best_planet['ships'][2]/6,
                )


if __name__ == "__main__":
    # open the connection and login
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('rps.qr4.dev', 6000))
    io = s.makefile('rw')
    write(io, 'login %s %s' % (USERNAME, PASSWORD))

    # main game loop
    while 1:
        data = io.readline().strip()
        if not data:
            print("no data")
            continue
        elif data[0] == "{":
            state = json.loads(data)
            if state['winner'] is not None or state['game_over']:
                print("Game Over.")
                break

            compute_move(io, state)
        else:
            print(data)
            if data == "invalid login":
                break

    s.close()
