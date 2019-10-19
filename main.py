import re
import os
import gzip
import time
import errno
import eventlet
import simplejson as json
import random
import subprocess
from collections import OrderedDict

from eventlet.green import socket
import redis

from engine import Engine

redis_url = os.environ.get('REDIS_URL') or 'localhost'
redis = redis.Redis(host=redis_url)
pool = eventlet.GreenPool()

COMMAND_DEADLINE = 6
MAX_ROUNDS = 500
START_ELO = 1000
MATCHMAKING_INTERVAL = 1

redis.ping()

class Authenticator(object):
    def check(self, username, password):
        saved_password = redis.get("user:%s" % username)
        if not saved_password:
            if len(username) > 20:
                return False
            redis.set("user:%s" % username, password)
            return True
        return saved_password == password

Authenticator = Authenticator()

class Scoreboard(object):
    def update_victory(self, winner, loser):
        return self.update_elo(winner, loser, 1.0, 0.0)

    def update_draw(self, player1, player2):
        return self.update_elo(player1, player2, 0.5, 0.5)

    def update_elo(self, p_a, p_b, score_a, score_b):
        Ra = redis.zscore('elo', p_a) or START_ELO
        Rb = redis.zscore('elo', p_b) or START_ELO
        Ea = 1.0 / (1 + 10.0 ** ((Rb - Ra)/400.0))
        Eb = 1.0 / (1 + 10.0 ** ((Ra - Rb)/400.0))
        Ra_new = Ra + 10 * (score_a - Ea)
        Rb_new = Rb + 10 * (score_b - Eb)
        redis.zadd('elo', {p_a: Ra_new})
        redis.zadd('elo', {p_b: Rb_new})
        return Ra_new, Rb_new, Ra_new - Ra

    def get_score(self, player):
        return redis.zscore('elo', player) or START_ELO

Scoreboard = Scoreboard()

class Player(object):
    def __init__(self, conn, username):
        self.conn = conn

        self.username = username
        self.cmd_issued = False

        self.game = None
        self.player_id = None

    def get_score(self):
        return Scoreboard.get_score(self.username)

    def send(self, msg):
        if self.conn:
            self.conn.send(msg)

    def connection_lost(self):
        if self.game and not self.game.game_over:
            self.disqualify("connection lost")
        else:
            self.conn.disconnect()

    def disqualify(self, reason):
        print "player %r disqualified: %s" % (self, reason)
        other_player = self.game.other_player(self)
        self.game.game_end(
            other_player.player_id,
            "player %d disqualified: %s" % (self.player_id, reason)
        )

    def cmd_nop(self):
        # print "player %r nop" % self
        if self.game.game_over:
            self.send("game is over. please disconnect")
            return
        if self.cmd_issued:
            self.disqualify("sent more than one command")
            return
        self.cmd_issued = True
        self.send("command received. waiting for other player...")
        self.game.check_round_finished()

    def cmd_send_fleet(self, origin_id, target_id, a, b, c):
        # print "player %r fleet %d->%d (%d,%d,%d = %d)" % (self, origin_id, target_id, a, b, c, a+b+c)
        if self.game.game_over:
            self.send("game is over. please disconnect")
            return
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
        self.game_id = redis.incr('game_id')

        print "starting game %r" % self.game_id

        self.game_log_name = "log/%08d/%04d.json" % (self.game_id / 1000, self.game_id % 1000)
        try:
            os.makedirs(os.path.dirname(self.game_log_name))
        except OSError, err:
            if err.errno != errno.EEXIST:
                raise
        self.game_log = file(self.game_log_name, "wb")

        self.players = players

        self.game_over = False
        self.winner = None

        for idx, player in enumerate(self.players):
            player.game = self
            player.player_id = idx + 1

        for player in self.players:
            player.send("game %d starts. other player is %s" % (self.game_id, self.other_player(player).username))

        self.engine = Engine(max_rounds=MAX_ROUNDS)

        self.send_state()
        self.deadline = eventlet.greenthread.spawn_after(COMMAND_DEADLINE, self.deadline_reached)

        p = redis.pipeline()
        p.hset('game:%d' % self.game_id, 'p1', self.players[0].username)
        p.hset('game:%d' % self.game_id, 'p2', self.players[1].username)

        p.rpush('games', self.game_id)

        p.rpush('player:%s:games' % self.players[0].username, self.game_id)
        p.rpush('player:%s:games' % self.players[1].username, self.game_id)
        p.execute()

    def other_player(self, player):
        return self.players[1 - self.players.index(player)]

    def has_player(self, player):
        return player in self.players

    def game_end(self, winner, reason):
        assert not self.game_over

        print "game ends: winner is %s: %s" % (winner, reason)

        if self.deadline is not None:
            self.deadline.cancel()
            self.deadline = None

        self.game_over = True
        self.winner = winner

        if winner is None:
            elo_p1, elo_p2, elo_diff = Scoreboard.update_draw(
                self.players[0].username,
                self.players[1].username
            )
        elif winner == 1:
            elo_p1, elo_p2, elo_diff = Scoreboard.update_victory(
                self.players[0].username,
                self.players[1].username
            )
        else:
            elo_p2, elo_p1, elo_diff = Scoreboard.update_victory(
                self.players[1].username,
                self.players[0].username
            )
            elo_diff = - elo_diff

        self.players[0].send("game ended: %s, %.2f ELO for you. final state follows" % (reason, elo_diff))
        self.players[1].send("game ended: %s, %.2f ELO for you. final state follows" % (reason, -elo_diff))

        self.send_state()

        for player in self.players:
            player.send("This game is now available at http://rps.vhenne.de/game/%d" % self.game_id)

        self.game_log.close()

        # This unlinks the gziped file after compressing
        subprocess.call(["gzip", "-f", self.game_log_name])

        p = redis.pipeline()
        p.hset('game:%d' % self.game_id, 'end', int(time.time()))
        p.hset('game:%d' % self.game_id, 'elodiff', elo_diff)

        p.zadd('scoreboard', {self.players[0].username: -elo_p1})
        p.zadd('scoreboard', {self.players[1].username: -elo_p2})
        p.execute()

        def disconnect():
            self.players[0].conn.disconnect()
            self.players[1].conn.disconnect()
        eventlet.greenthread.spawn_after(1, disconnect)


    def check_round_finished(self):
        # pruefen, ob beide spieler befehle abgegeben haben...
        for player in self.players:
            if not player.cmd_issued:
                return

        self.deadline.cancel() # abort deadline countdown
        self.deadline = None

        for player in self.players:
            player.send("calculating round")
        self.engine.do_round()

        if self.engine.winner is not None:
            if self.engine.winner == "draw":
                self.game_end(
                    None,
                    "game is a draw"
                )
            else:
                self.game_end(
                    self.engine.winner,
                    "player %d won" % self.engine.winner
                )
            return

        self.send_state()

        for player in self.players:
            player.send("waiting for you command")

        self.deadline = eventlet.greenthread.spawn_after(COMMAND_DEADLINE, self.deadline_reached)
        for player in self.players:
            player.cmd_issued = False

    def deadline_reached(self):
        if not self.players[0].cmd_issued and not self.players[1].cmd_issued:
            self.game_end(
                None,
                "both players failed to send a command"
            )
        else:
            for player in self.players:
                if not player.cmd_issued:
                    player.disqualify("no command sent")

    def get_player_state(self, for_player):
        state = self.engine.dump()
        state['player_id'] = for_player.player_id
        state['game_over'] = self.game_over
        state['winner'] = self.winner
        state['players'] = [
            OrderedDict([
                ('id', player.player_id),
                ('name', player.username),
                ('itsme', player == for_player),
            ]) for player in self.players
        ]
        return state

    def get_log_state(self):
        state = self.engine.dump()
        state['game_over'] = self.game_over
        state['winner'] = self.winner
        state['players'] = [
            OrderedDict([
                ('id', player.player_id),
                ('name', player.username),
            ]) for player in self.players
        ]
        return state

    def send_state(self):
        for player in self.players:
            player.send(json.dumps(self.get_player_state(player)))
        self.game_log.write(json.dumps(self.get_log_state()))
        self.game_log.write("\n")
        self.game_log.flush()

class MatchMaking(object):
    def __init__(self):
        self.lobby = []

    def add_player(self, player):
        self.lobby.append(player)

    def remove_player(self, player):
        if player in self.lobby:
            self.lobby.remove(player)

    def check_should_game_start(self):
        pairing = []
        for player in self.lobby:
            pairing.append((player.get_score(), player))
        pairing.sort()

        while len(pairing) >= 2:
            first_idx = random.randint(0, len(pairing)-1)
            while 1:
                second_idx = int(random.gauss(first_idx, 2))
                second_idx = max(0, min(len(pairing) - 1, second_idx))
                if second_idx != first_idx:
                    break
            if first_idx > second_idx:
                first_idx, second_idx = second_idx, first_idx
            (elo1, player1), (elo2, player2) = pairing.pop(second_idx), pairing.pop(first_idx)
            print "sending %s (%f) and %s (%f) into game" % (
                player1, elo1, player2, elo2)
            Game([player1, player2])

        # uebriggebliebenen Spieler ist nun die neue Lobby
        self.lobby = [player for _, player in pairing]

    def dump(self):
        print "%d player in lobby" % len(self.lobby)

MatchMaking = MatchMaking()

class Connection(object):
    def __init__(self, socket):
        self.socket = socket
        self.read_file = socket.makefile('r')
        self.write_queue = eventlet.queue.Queue()
        self.player = None
        self.reader_thread = pool.spawn(self.reader)
        pool.spawn_n(self.writer)

    def handle_cmd_login(self, username, password):
        if self.player:
            self.send("already logged in")
            return

        if not Authenticator.check(username, password):
            self.send("invalid login")
            return

        self.player = Player(self, username)
        self.send("your current score: %.2f. waiting for game start..." % self.player.get_score())
        MatchMaking.add_player(self.player)

    def handle_cmd_send(self, origin_id, target_id, a, b, c):
        if self.player is None:
            self.send("login first")
            return

        if self.player.game is None:
            self.send("not in a game. please wait")
            return

        try:
            origin_id, target_id, a, b, c = int(origin_id), int(target_id), int(a), int(b), int(c)
        except ValueError:
            self.send("numbers expected")
            return

        self.player.cmd_send_fleet(origin_id, target_id, a, b, c)

    def handle_cmd_nop(self):
        if self.player is None:
            self.send("login first")
            return

        if self.player.game is None:
            self.send("not in a game. please wait")
            return

        self.player.cmd_nop()

    def handle_cmd_quit(self):
        self.disconnect()

    def handle_connection_lost(self):
        if self.player:
            MatchMaking.remove_player(self.player)
            self.player.connection_lost()
        else:
            self.disconnect()

    def disconnect(self):
        self.send("closing connection. see you next time")
        self.write_queue.put(None) # signal eof to writer

        print "reader closed"
        self.read_file.close()
        self.reader_thread.kill()
        # no code here: the kill might prevent this from being reached

    def send(self, msg):
        self.write_queue.put(msg + "\n")

    def read_tokens(self):
        line = self.read_file.readline().strip()

        if not line: # eof
            return None

        if not re.match("^[a-z 0-9A-Z_\-]*$", line):
            self.send("Invalid data received. Valid bytes: [a-z 0-9A-Z_\-]")
            return None

        return [token.strip().lower() for token in line.split() if token]

    def reader(self):
        while 1:
            tokens = self.read_tokens()
            if tokens is None:
                self.handle_connection_lost()
                return # never reached. this thread is killed
            elif not tokens: # empty?
                continue
            cmd, args = tokens[0], tokens[1:]
            handler = getattr(self, "handle_cmd_%s" % cmd, None)
            if handler is None:
                self.send("unknown command: %r" % cmd)
            else:
                try:
                    handler(*args)
                except TypeError, err:
                    self.send("invalid arguments: %s" % err)

    def writer(self):
        while 1:
            data = self.write_queue.get()
            if data is None: # should close write side
                break
            try:
                self.socket.send(data)
            except socket.error:
                break

        print "writer closed"
        try:
            self.socket.shutdown(socket.SHUT_WR)
        except socket.error:
            pass
        self.socket.close()

    def __repr__(self):
        return "<Connection: %r>" % (self.player,)

def status():
    while 1:
        eventlet.greenthread.sleep(2)
        MatchMaking.dump()

def check_match():
    while 1:
        eventlet.greenthread.sleep(MATCHMAKING_INTERVAL)
        MatchMaking.check_should_game_start()

def main():
    server = eventlet.listen(('0.0.0.0', 6000))
    pool.spawn_n(status)
    pool.spawn_n(check_match)

    while 1:
        try:
            socket, address = server.accept()
            conn = Connection(socket)
            conn.send("welcome to rocket-paper-spacegoo. see https://github.com/qr4/rocket-paper-spacegoo for more information on how to play")
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()
