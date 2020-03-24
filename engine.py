from collections import OrderedDict
from scipy.spatial import Delaunay
from math import *
import random

MAX_PRODUCTION_ROUNDS = 100


class Planet():
    def __init__(self,id,owner_id,production,posx,posy):
        self.id = id
        self.owner_id = owner_id
        self.production_rounds = 0
        self.production = production
        self.ships = [s*10 + 10 for s in production]
        self.posx = posx
        self.posy = posy

    def distance(self,other_planet):
        xdiff = self.posx - other_planet.posx
        ydiff = self.posy - other_planet.posy
        return int(ceil(sqrt(xdiff*xdiff + ydiff*ydiff)))

    def dump(self):
        state = OrderedDict([
            ("id", self.id),
            ("x", self.posx),
            ("y", self.posy),
            ("owner_id", self.owner_id),
            ("ships", self.ships),
            ("production", self.production),
            ("production_rounds_left", max(MAX_PRODUCTION_ROUNDS - self.production_rounds, 0))
        ])
        return state

def battle_round(attacker,defender):
    # only an asymetric round. this needs to be called twice
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


def battle(s1,s2):
    ships1 = s1[::]
    ships2 = s2[::]
    while sum(ships1) > 0 and sum(ships2) >0:
        new1 = battle_round(ships2,ships1)
        ships2 = battle_round(ships1,ships2)
        ships1 = new1

    ships1 = list(map(int,ships1))
    ships2 = list(map(int,ships2))
    return ships1, ships2


class Fleet():
    def __init__(self,id,owner_id,origin,target,ships,current_round):
        self.eta = current_round + origin.distance(target)
        self.origin = origin
        self.target = target
        self.ships = list(map(lambda want, onplanet: min(max(want,0),onplanet), ships,origin.ships))
        origin.ships = list(map(lambda infleet,onplanet: onplanet-infleet, self.ships,origin.ships))
        self.id = id
        self.owner_id = owner_id
        self.alive = True

    def land(self):
        # print "fleet landing"
        if self.target.owner_id == self.owner_id:
            self.target.ships = list(map(lambda infleet,onplanet: infleet+onplanet, self.ships,self.target.ships))
        else:
            #battle!
            attacker,defender = battle(self.ships,self.target.ships)
            if sum(defender) > 0:
                #defended!
                self.target.ships = defender
            else:
                #invasion successful!
                self.target.ships = attacker
                self.target.owner_id = self.owner_id

    def dump(self):
        state = OrderedDict([
             ("id", self.id),
             ("owner_id", self.owner_id),
             ("ships", self.ships),
             ("origin", self.origin.id),
             ("target", self.target.id),
             ("eta", self.eta),
             ("alive", self.alive)
        ])
        return state

    def combine(self, other):
        for idx, count in enumerate(other.ships):
            self.ships[idx] += count

    def battle(self, other):
        self_ships, other_ships = battle(self.ships,other.ships)
        self.ships = self_ships
        other.ships = other_ships

        if sum(other_ships) > 0:
            # we died
            self.alive = False
        else:
            other.alive = False


class Engine():

    def insert_symmetric_planets(self,posx,posy,production,start_planets = False):
        owner0, owner1 = 0,0
        if start_planets:
            owner0, owner1 = 1,2

        self.planets.append(Planet(len(self.planets),owner0,production,posx,posy))
        self.planets.append(Planet(len(self.planets),owner1,production,-posx,-posy))

    def insert_central_planet(self,production):
        self.planets.append(Planet(len(self.planets),0,production,0,0))


    def generate_planet(self):
        type = random.randint(0,2)
        production = [0]*3
        if type == 0: #one kind only
            production = [max(1,int(abs(random.gauss(2,5)))),0,0]
        elif type == 1: #two kinds of ships
            production = [max(1,int(abs(random.gauss(1,4)))),max(1,int(abs(random.gauss(1,4)))),0]
        else: # three kinds of ships
            if random.randint(0,1) == 0:
                production = [max(1,int(abs(random.gauss(0,3)))),max(1,int(abs(random.gauss(0,3)))),max(1,int(abs(random.gauss(0,3))))]
            else:
                production = [max(1,int(abs(random.gauss(0,3))))]*3
        random.shuffle(production)
        return production


    def does_planet_fit(self,x,y):
        mindist = 100023
        for planet in self.planets:
            xdiff = x-planet.posx
            ydiff = y-planet.posy
            dist = sqrt(xdiff*xdiff + ydiff*ydiff)
            mindist = min(mindist,dist)
        return (mindist > 5.0)

    def find_fitting_position(self,max_x, max_y):
        x = 0
        y = 0
        while not self.does_planet_fit(x, y):
            x = random.randint(-max_x,max_x)
            y = random.randint(-max_y,max_y)
        return x,y

    def generate_map(self):
        max_x = 20
        max_y = 15
        num_planets = random.randint(2,10)

        self.insert_central_planet(self.generate_planet())
        for i in range(0,num_planets):
            x,y = self.find_fitting_position(max_x, max_y)
            self.insert_symmetric_planets(x,y,self.generate_planet(), start_planets=((i==0) or (i < num_planets/2) and (random.randint(0,10) < 2)))

        points = [[planet.posx, planet.posy] for planet in self.planets]
        for tri in Delaunay(points).simplices:
            for i in range(3):
                pt1 = tri[i]
                pt2 = tri[(i+1)%3]
                self.hyperlanes.append([int(pt1), int(pt2)])
                self.hyperlanes.append([int(pt2), int(pt1)])

    def __init__(self,max_rounds = 500):
        self.planets = []
        self.hyperlanes = []
        self.generate_map()
        self.fleets = []
        self.round = 0
        self.next_fleet_id = 0
        self.max_rounds = max_rounds
        self.winner = None #can also be "draw" or a player_id

    def send_fleet(self,player_id,origin_id,target_id,ships):
        if not (0 <= origin_id < len(self.planets)):
            return
        if not (0 <= target_id < len(self.planets)):
            return
        if origin_id == target_id:
            return
        if sum(ships) == 0:
            return

        origin = self.planets[origin_id]
        target = self.planets[target_id]


        if not player_id == origin.owner_id:
            return

        new_fleet = Fleet(self.next_fleet_id, player_id, origin, target,ships,self.round)
        if sum(new_fleet.ships) == 0:
            return

        self.fleets.append(new_fleet)
        self.next_fleet_id+=1


    def do_round(self):
        for i,planet in enumerate(self.planets):
            # print "planet ", i, "owner ", planet.owner_id, " :"
            if not planet.owner_id == 0 and planet.production_rounds is not MAX_PRODUCTION_ROUNDS:
                planet.production_rounds += 1
                planet.ships = list(map(lambda s,p: s+p, planet.ships, planet.production))
            # print planet.ships

        players_alive = []
        land_on_planet = {}
        for fleet in self.fleets[:]:
            player = fleet.owner_id
            # print("fleet ", fleet.id, ", owner ", fleet.owner_id, ", eta ", fleet.eta)
            if not player in players_alive:
                players_alive.append(player)
            if fleet.eta == self.round:
                self.fleets.remove(fleet)
                # combine fleets before battling
                if fleet.target not in land_on_planet:
                    land_on_planet[fleet.target] = []
                land_on_planet[fleet.target].append(fleet)

        for planet, fleets in land_on_planet.items():
            # print("landing fleets on ", planet)
            fleets_of_players = {}
            for fleet in fleets:
                if fleet.owner_id not in fleets_of_players:
                    fleets_of_players[fleet.owner_id] = []
                fleets_of_players[fleet.owner_id].append(fleet)

            # combine the fleets
            for key, playerfleets in fleets_of_players.items():
                if len(playerfleets) > 1:
                    for other in playerfleets[1:]:
                        playerfleets[0].combine(other)


            survivor = None
            # check if there are multiple players landing the same time. If so, let them battle first
            keys = list(fleets_of_players.keys())
            if len(keys) > 1:
                # print("more than one player!", fleets_of_players)
                if len(keys) > 2:
                    print("ERROR! more than 2 different playes landed on the planet")

                p1 = fleets_of_players[keys[0]][0]
                p2 = fleets_of_players[keys[1]][0]

                p1.battle(p2)

                if p1.alive:
                    survivor = p1
                elif p2.alive:
                    survivor = p2

            else:
                survivor = fleets_of_players[keys[0]][0]


            if survivor:
                survivor.land()

        for planet in self.planets:
            player = planet.owner_id
            if not player == 0 and not player in players_alive:
                players_alive.append(player)

        self.round +=1

        if len(players_alive) == 1:
            self.winner = players_alive[0]
            # print "WINNER: ", self.winner
            return

        if self.round >= self.max_rounds:
            self.winner = "draw"
            # print "DRAW!"
            return


    def dump(self):
        state = OrderedDict([
            ("planets", [p.dump() for p in self.planets]),
            ("fleets", [f.dump() for f in self.fleets]),
            ("round", self.round),
            ("max_rounds", self.max_rounds),
            ("hyperlanes", self.hyperlanes)
        ])
        return state


if __name__ == "__main__":
    engine = Engine()
    engine.do_round()
    print(engine.dump())

