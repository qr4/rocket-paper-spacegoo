from collections import OrderedDict
from math import *

  
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
    #das gute 3,1,1-schema.
    #nur eine asymmetrische runde. das hier muss mal also zweimal aufrufen.
    numships = len(attacker)
    defender = defender[::]
    for def_type in range(0,numships):
        for att_type in range(0,numships):
            multiplier = 1
            if (def_type-att_type)%numships == 1:
                multiplier = 3
            if attacker[att_type] <= 0:
                multiplier = 0
            defender[def_type] -= multiplier
        defender[def_type] = max(0,defender[def_type])
    return defender
    
    
def battle(s1,s2):
    ships1 = s1[::]
    ships2 = s2[::]
    while sum(ships1) > 0 and sum(ships2) >0:
        new1 = battle_round(ships2,ships1)
        ships2 = battle_round(ships1,ships2)
        ships1 = new1
        print ships1,ships2
        
    return ships1, ships2
        #new2 = ships2
        
        

    
class Fleet():
    def __init__(self,id,owner_id,origin,target,ships,current_round):
        self.eta = current_round + origin.distance(target)
        self.origin = origin
        self.target = target
        self.ships = map(lambda want, onplanet: min(want,onplanet), ships,origin.ships)
        origin.ships = map(lambda infleet,onplanet: onplanet-infleet, self.ships,origin.ships)
        self.id = id
        self.owner_id = owner_id
    
    def land(self):
        print "fleet landing"
        if self.target.owner_id == self.owner_id:
            self.target.ships = map(lambda infleet,onplanet: infleet+onplanet, self.ships,self.target.ships)
        else:
            #battle!
            attacker,defender = battle(self.ships,self.target.ships)
            if sum(defender) > 0:
                #defended!
                print "ZOMG defended"
                self.target.ships = defender
            else:
                #invasion successful!
                print "ZOMG invasion successful"
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
        
        
        

class Engine():
    def generate_map(self):
        
        self.planets.append(Planet(len(self.planets),0,[1,1,1],0,0))
        
        self.planets.append(Planet(len(self.planets),1,[10,20,30],-1,-2))
        
        self.planets.append(Planet(len(self.planets),2,[1,2,3],1,2))
        
        
        
        
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
        print "DINGDINGDING ROUND ", self.round
        
        for i,planet in enumerate(self.planets):
            print "planet ", i, "owner ", planet.owner_id, " :"
            if not planet.owner_id == 0:
                planet.ships = map(lambda s,p: s+p, planet.ships, planet.production)
            print planet.ships
        
        players_alive = []
        for fleet in self.fleets:
            player = fleet.owner_id
            print "fleet ", fleet.id, ", owner ", fleet.owner_id, ", eta ", fleet.eta
            if not player in players_alive:
                players_alive.append(player)
            if fleet.eta == self.round:
                self.fleets.remove(fleet)
                fleet.land()
                
        for planet in self.planets:
            player = planet.owner_id
            if not player == 0 and not player in players_alive:
                players_alive.append(player)
        
        if len(players_alive) == 1:
            self.winner = players_alive[0]
            print "WINNER: ", self.winner
            return
        
        if self.round >= self.max_rounds:
            self.winner = "draw"
            print "DRAW!"
            return
            
        self.round +=1
            
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
    engine.send_fleet(1, 1, 2, [200,300,400])
    engine.do_round()
    engine.do_round()
    engine.do_round()
    engine.do_round()
    print engine.dump()
    engine.do_round()
    engine.do_round()
    engine.do_round()
    print engine.dump()
    
    
    
