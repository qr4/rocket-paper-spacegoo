import eventlet
import json
from collections import OrderedDict
from engine import Engine

COMMAND_DEADLINE = 3

class Player(object):
    def __init__(self, conn, username):
        self.conn = conn

        self.username = username
        self.cmd_issued = False
        self.win = False
        self.lose = False

        self.game = None
        self.player_id = None

    def connection_lost(self):
        self.conn = None

    def send(self, msg):
        if self.conn:
            self.conn.send(msg)

    def disqualify(self, reason):
        print "player %r disqualified: %s" % (self, reason)
        self.send("you were disqualified: %s" % reason)
        self.game.other_player(self).send("other player was disqualified: %s" % reason)
        self.game.game_over = True
        self.lose = True
        self.game.send_state()

    def cmd_nop(self):
        print "player %r nop" % self
        if self.cmd_issued:
            self.disqualify("sent more than one command")
            return
        self.cmd_issued = True
        self.send("command received. waiting for other player...")
        self.game.check_round_finished()

    def cmd_send_fleet(self, origin_id, target_id, a, b, c):
        print "player %r fleet %d->%d (%d,%d,%d = %d)" % (self, origin_id, target_id, a, b, c, a+b+c)
        if self.cmd_issued:
            self.disqualify("sent more than one command")
            return
        self.cmd_issued = True
        self.send("command received. waiting for other player...")
        self.game.engine.send_fleet(self.player_id, origin_id, target_id, [a,b,c])
        self.game.check_round_finished()

    def __repr__(self):
        return "<Player %s>" % (self.username)

class Game(object):
    def __init__(self, players):
        assert len(players) == 2
        self.players = players
        self.game_over = False

        for idx, player in enumerate(self.players):
            player.game = self
            player.player_id = idx + 1
        
        for player in self.players:
            player.send("game starts. other player is %s" % self.other_player(player).username)

        self.engine = Engine(max_rounds=500)

        self.send_state()
        self.deadline = eventlet.greenthread.spawn_after(COMMAND_DEADLINE, self.deadline_reached)

    def is_abandoned(self):
        return all(player.conn is None for player in self.players)

    def other_player(self, player):
        return self.players[1 - self.players.index(player)]

    def has_player(self, player):
        return player in self.players

    def check_round_finished(self):
        for player in self.players:
            if not player.cmd_issued:
                return
        self.deadline.cancel() # abort deadline countdown
        for player in self.players:
            player.send("round starts")
        self.engine.do_round()
        self.send_state()
        self.deadline = eventlet.greenthread.spawn_after(COMMAND_DEADLINE, self.deadline_reached)
        for player in self.players:
            player.cmd_issued = False

    def deadline_reached(self):
        for player in self.players:
            if not player.cmd_issued:
                player.disqualify("no command sent")
        
    def get_state(self, for_player):
        state = self.engine.dump()
        state['player_id'] = for_player.player_id
        state['status'] = self.engine.winner
        state['players'] = [
            OrderedDict([
                ('id', player.player_id),
                ('name', player.username),
                ('won', player.win),
                ('lost', player.lose),
                ('itsme', player == for_player),
            ]) for player in self.players
        ]
        return state

    def send_state(self):
        for player in self.players:
            state = self.get_state(player)
            player.send(json.dumps(state))

    def end(self):
        if self.deadline:
            self.deadline.cancel()


class Authenticator(object):
    def __init__(self):
        pass

    def check(self, username, password):
        return True

Authenticator = Authenticator()

class MatchMaking(object):
    def __init__(self):
        self.lobby = []
        self.games = []

    def add_player(self, player):
        self.lobby.append(player)
        self.check_should_game_start()

    def remove_player(self, player):
        if player in self.lobby:
            self.lobby.remove(player)

        player.connection_lost()

        game = player.game
        if game:
            player.disqualify("connection lost")
            if game.is_abandoned():
                print "game abandoned"
                self.games.remove(game)

    def check_should_game_start(self):
        if len(self.lobby) >= 2:
            player1, player2 = self.lobby.pop(), self.lobby.pop()
            self.games.append(Game([player1, player2]))

    def dump(self):
        print "%d player in lobby, %d running games" % (
            len(self.lobby), len(self.games))

MatchMaking = MatchMaking()

def cmd_dispatch(queue):
    while 1:
        conn, cmd, args = queue.get()
        if cmd == "login":
            if conn.player:
                conn.send("already logged in")
                continue

            if len(args) != 2:
                conn.send("invalid arguments")
                continue

            username, password = args
            if not Authenticator.check(username, password):
                conn.send("invalid login")
                continue

            player = Player(conn, username)
            conn.player = player
            conn.send("waiting for game start...")
            MatchMaking.add_player(player)
        elif cmd == "send":
            if len(args) != 5:
                conn.send("invalid arguments")
                continue

            try:
                origin_id, target_id, a, b, c = map(int, args)

            except ValueError:
                conn.send("numbers expected")
                continue

            if conn.player is None:
                conn.send("login first")
                continue

            conn.player.cmd_send_fleet(origin_id, target_id, a, b, c)
        elif cmd == "nop":
            if conn.player is None:
                conn.send("login first")
                continue

            conn.player.cmd_nop()
        elif cmd == "quit":
            if conn.player:
                MatchMaking.remove_player(conn.player)
        else:
            conn.send("unknown command")




class Connection(object):
    def __init__(self, socket, game_queue):
        self.socket = socket
        self.read_file = socket.makefile('r')
        self.game_queue = game_queue
        self.out_queue = eventlet.queue.Queue()
        self.player = None

    def read_tokens(self):
        line = self.read_file.readline()

        if not line: # eof
            return None

        return [token.strip().lower() for token in line.split() if token]

    def send(self, msg):
        self.out_queue.put(msg + "\n")

    def reader(self):
        while 1:
            tokens = self.read_tokens()
            if tokens is None or (tokens and tokens[0] == "quit"): # eof or quit
                self.game_queue.put((self, "quit", []))
                self.out_queue.put(None) # signal eof to writer
                break
            elif not tokens: # empty?
                continue
            cmd, args = tokens[0], tokens[1:]
            self.game_queue.put((self, cmd, args))
        print "reader closed"
        self.read_file.close()

    def writer(self):
        while 1:
            data = self.out_queue.get()
            if data is None: # should close write side
                break
            self.socket.send(data)
        print "writer closed"
        self.socket.close()

    def __repr__(self):
        return "<Connection: %r>" % (self.username,)

def status():
    while 1:
        eventlet.greenthread.sleep(2)
        MatchMaking.dump()

def main():
    server = eventlet.listen(('0.0.0.0', 6000))
    pool = eventlet.GreenPool()
    queue = eventlet.queue.Queue()
    pool.spawn_n(cmd_dispatch, queue)
    pool.spawn_n(status)

    while 1:
        try:
            socket, address = server.accept()
            conn = Connection(socket, queue)
            pool.spawn_n(conn.reader)
            pool.spawn_n(conn.writer)
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
