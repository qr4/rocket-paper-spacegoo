import eventlet
import json
from game import Game as Engine

COMMAND_DEADLINE = 30

class Player(object):
    def __init__(self, conn, username):
        self.conn = conn
        conn.player = self

        self.username = username
        self.cmd_issued = False
        self.win = False
        self.lose = False

        self.game = None
        self.player_id = None

    def send(self, msg):
        self.conn.send(msg)

    def disqualify(self, reason):
        self.send("you were disqualified: %s" % reason)
        self.game.other_player(self).send("other player was disqualified: %s" % reason)
        self.game.game_over = True
        self.lose = True

    def cmd_nop(self):
        if self.cmd_issued:
            self.disqualify("sent more than one command")
            return
        self.cmd_issued = True
        self.send("command received. waiting for other player...")
        self.game.check_round_finished()

    def cmd_send_fleet(self, origin_id, target_id, a, b, c):
        if self.cmd_issued:
            self.disqualify("sent more than one command")
            return
        self.cmd_issued = True
        self.send("command received. waiting for other player...")
        self.game.engine.send_fleet(self.player_id, origin_id, target_id, [a,b,c])
        self.game.check_round_finished()

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

        self.engine = Engine()
        self.engine.generate_map()

        self.send_state()

    def other_player(self, player):
        return self.players[1 - self.players.index(player)]

    def has_player(self, player):
        return player in self.players

    def check_round_finished(self):
        for player in self.players:
            if not player.cmd_issued:
                return
        self.deadline.cancel() # abort deadline countdown
        self.deadline = None
        for player in self.players:
            player.send("round starts")
        self.engine.do_round()
        self.send_state()

    def deadline_reached(self):
        for player in self.players:
            if not player.cmd_issued:
                player.disqualify("no command sent")
        
    def get_state(self):
        return self.engine.dump()

    def send_state(self):
        state = self.get_state()
        for player in self.players:
            player.send(json.dumps(state))
        self.deadline = eventlet.greenthread.spawn_after(COMMAND_DEADLINE, self.deadline_reached)
        for player in self.players:
            player.cmd_issued = False

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
        for game in self.games:
            if game.has_player(player):
                game.player_disappears(player)
                self.games.remove(game)
                break

    def check_should_game_start(self):
        if len(self.lobby) >= 2:
            player1, player2 = self.lobby.pop(), self.lobby.pop()
            self.games.append(Game([player1, player2]))

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
            MatchMaking.remove_player(player)
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

def main():
    server = eventlet.listen(('0.0.0.0', 6000))
    pool = eventlet.GreenPool()
    queue = eventlet.queue.Queue()
    pool.spawn_n(cmd_dispatch, queue)

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
