from collections import OrderedDict
from math import *
import random


class Planet():
    def __init__(self,id,owner_id,production,posx,posy):
        self.id = id
        self.owner_id = owner_id
        self.production = production
        self.ships = map(lambda s: s*10 + 10, production)
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
            ("production", self.production)
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
        #print ships1,ships2

    ships1 = map(int,ships1)
    ships2 = map(int,ships2)
    #print ships1,ships2
    return ships1, ships2


class Fleet():
    def __init__(self,id,owner_id,origin,target,ships,current_round):
        self.eta = current_round + origin.distance(target)
        self.origin = origin
        self.target = target
        self.ships = map(lambda want, onplanet: min(max(want,0),onplanet), ships,origin.ships)
        origin.ships = map(lambda infleet,onplanet: onplanet-infleet, self.ships,origin.ships)
        self.id = id
        self.owner_id = owner_id

    def land(self):
        # print "fleet landing"
        if self.target.owner_id == self.owner_id:
            self.target.ships = map(lambda infleet,onplanet: infleet+onplanet, self.ships,self.target.ships)
        else:
            #battle!
            attacker,defender = battle(self.ships,self.target.ships)
            if sum(defender) > 0:
                #defended!
                # print "ZOMG defended"
                self.target.ships = defender
            else:
                #invasion successful!
                # print "ZOMG invasion successful"
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
        ])
        return state

    def combine(self, other):
        for idx, count in enumerate(other.ships):
            self.ships[idx] += count

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
        print production
        return production


    def does_planet_fit(self,x,y):
        mindist = 100023
        for planet in self.planets:
            xdiff = x-planet.posx
            ydiff = y-planet.posy
            dist = sqrt(xdiff*xdiff + ydiff*ydiff)
            mindist = min(mindist,dist)
        return (mindist > 3.0)

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

        #print self.planets

    def __init__(self,max_rounds = 500):
        self.planets = []
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
        origin = self.planets[origin_id]
        target = self.planets[target_id]


        if not player_id == origin.owner_id:
            return

        self.fleets.append(Fleet(self.next_fleet_id, player_id, origin, target,ships,self.round))
        self.next_fleet_id+=1


    def do_round(self):
        # print "DINGDINGDING ROUND ", self.round

        for i,planet in enumerate(self.planets):
            # print "planet ", i, "owner ", planet.owner_id, " :"
            if not planet.owner_id == 0:
                planet.ships = map(lambda s,p: s+p, planet.ships, planet.production)
            # print planet.ships

        players_alive = []
        land_on_planet = {}
        highest_owner = 1
        for fleet in self.fleets[:]:
            player = fleet.owner_id
            # print "fleet ", fleet.id, ", owner ", fleet.owner_id, ", eta ", fleet.eta
            if not player in players_alive:
                players_alive.append(player)
            if fleet.eta == self.round:
                self.fleets.remove(fleet)
                # combine fleets before battling
                if fleet.target not in land_on_planet:
                    land_on_planet[fleet.target] = []
                land_on_planet[fleet.target].append(fleet)
                if fleet.owner_id > highest_owner: highest_owner = fleet.owner_id

        for planet, fleets in land_on_planet.iteritems():
            # print "landing fleets on ", planet
            fleets_of_players = [[] for _ in range(highest_owner + 1)]
            for fleet in fleets:
                fleets_of_players[fleet.owner_id].append(fleet)
            for playerfleets in fleets_of_players:
                if len(playerfleets) > 1:
                    for other in playerfleets[1:]:
                        playerfleets[0].combine(other)
                if playerfleets:
                    playerfleets[0].land()

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
            ("planets", map(lambda p: p.dump(), self.planets)),
            ("fleets", map(lambda f: f.dump(), self.fleets)),
            ("round", self.round),
            ("max_rounds", self.max_rounds),
        ])
        return state


if __name__ == "__main__":
    engine = Engine()
    engine.do_round()
    print engine.dump()

