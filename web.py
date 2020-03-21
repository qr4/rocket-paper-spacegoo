import sys
import os
import gzip
import logging
from itertools import zip_longest

from flask import Flask, Response
from flask import render_template, jsonify, send_from_directory
from flask_cors import CORS
import redis


INACTIVE_COUNT = 100

redis_url = os.environ.get('REDIS_URL') or 'localhost'
redis = redis.Redis(host=redis_url)
redis.ping()

app = Flask(__name__, static_folder="app/build/static", template_folder="app/build")
CORS(app)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def make_game_list(game_ids):
    p = redis.pipeline()
    for game_id in game_ids:
        game_id = game_id.decode()
        p.hget('game:%s' % game_id, 'p1')
        p.hget('game:%s' % game_id, 'p2')
        p.hget('game:%s' % game_id, 'elodiff')
        p.hget('game:%s' % game_id, 'end')
    games = []
    for game_id, (player1, player2, elodiff, end) in zip(game_ids, grouper(p.execute(), 4)):
        if elodiff:
            elodiff = float(elodiff)
            if elodiff < 0:
                player1, player2 = player2, player1
                elodiff = -elodiff

        games.append(dict(
            player1 = player1,
            player2 = player2,
            elodiff = elodiff,
            game_id = game_id,
            end     = end,
        ))
    return games

def get_run_info(username = None):
    if username:
        rank = redis.zrank('scoreboard', username)
        highscore_first = max(0, rank - 10)

        p = redis.pipeline()
        p.zrange('scoreboard', highscore_first, highscore_first + 20, withscores=True)
        p.lrange('player:%s:games' % username, -40, -1)
        p.llen('player:%s:games' % username)
        raw_highscores, last_game_ids, num_games = p.execute()
    else:
        rank = None
        p = redis.pipeline()
        p.zrange('scoreboard', 0, 39, withscores=True)
        p.lrange('games', -40, -1)
        p.llen('games')
        raw_highscores, last_game_ids, num_games = p.execute()

    highscores = []
    for score_user, score in raw_highscores:
        p = redis.pipeline()
        p.lindex('player:%s:games' % score_user, -1)
        (last_game,) = p.execute()
        inactive = (int(last_game_ids[-1] or 0) - int(last_game or 0) > INACTIVE_COUNT)
        highscores.append([score_user, -score, inactive] )

    last_games = make_game_list(list(reversed(last_game_ids)))

    if username:
        return highscores, last_games, num_games, (rank+1), highscore_first
    else:
        return highscores, last_games, num_games


@app.route("/api/info.json")
def info():
    highscores, last_games, num_games = get_run_info()

    return jsonify(
        highscore_first = 0,
        highscores = highscores,
        last_games = last_games,
        num_games = num_games,
    )

@app.route("/api/player/<username>/latest_game.json")
def player_latest_game(username):
    p = redis.pipeline()
    p.lindex('player:%s:games' % username,-1)
    (last,) = p.execute()
    return jsonify(
        last = last,
    )

@app.route("/api/player/<username>/info.json")
def player_info(username):
    highscores, last_games, num_games, rank, highscore_first = get_run_info(username)

    return jsonify(
        rank = rank,
        highscore_first = highscore_first,
        highscores = highscores,
        username = username,
        last_games = last_games,
        num_games = num_games,
    )

class vec(list):
    def add_inplace(self, other):
        for idx, (a, b) in enumerate(zip(self, other)):
            self[idx] = a + b

@app.route("/api/game/<int:game_id>/info.json")
def game_info(game_id):
    p = redis.pipeline()
    p.hget('game:%s' % game_id, 'p1')
    p.hget('game:%s' % game_id, 'p2')
    p.hget('game:%s' % game_id, 'elodiff')
    player1, player2, elodiff = p.execute()

    rank1 = redis.zrank('scoreboard', player1)
    if rank1 is None:
        rank1 = -1
    else:
        rank1  = rank1 + 1
    rank2 = redis.zrank('scoreboard', player2)

    if rank2 is None:
        rank2 = -1
    else:
        rank2  = rank2+ 1


    game_log_name = "log/%08d/%04d.json" % (game_id / 1000, game_id % 1000)

    return jsonify(
        game_id = game_id,
        game_log_name = game_log_name,
        player1 = player1,
        player2 = player2,
        rank1 = rank1,
        rank2 = rank2,
        finished = elodiff is not None,
        elodiff = (float(elodiff) if elodiff else None),
    )

@app.route("/api/game/<int:game_id>/rounds/<int:fromround>")
def game_rounds(game_id, fromround):
    game_log_name = "log/%08d/%04d.json" % (game_id / 1000, game_id % 1000)
    game_log = None
    try:
        game_log = open(game_log_name, "rb")
    except IOError:
        game_log_name = game_log_name + ".gz"
        game_log = gzip.GzipFile(game_log_name, "rb")
    lines = [l.decode() for l in game_log.readlines()]
    return Response (
            response = "[" + ",".join(lines[fromround:]) + "]",
            status = 200,
            mimetype = "application/json",
        )

@app.route("/api/log/<path:log_path>")
def logs(log_path):
    game_log_name = "log/" + log_path
    try:
        game_log = open(game_log_name, "rb")
    except IOError:
        game_log_name = game_log_name + ".gz"
        game_log = gzip.GzipFile(game_log_name, "rb")
    lines = [l.decode() for l in game_log.readlines()]
    return Response (
            response = "[" + ",".join(lines) + "]",
            status = 200,
            mimetype = "application/json",
        )

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    path_dir = os.path.abspath("./app/build/")
    if path != "" and os.path.exists(os.path.join(path_dir, path)):
        return send_from_directory(os.path.join(path_dir), path)
    else:
        return send_from_directory(os.path.join(path_dir),'index.html')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    app.run(host='0.0.0.0', port=8080, debug=True)
