import sys
import logging
from itertools import izip_longest, izip

from flask import Flask
from flask import render_template
import redis

redis = redis.Redis(host='localhost')

app = Flask(__name__)

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def make_game_list(game_ids):
    p = redis.pipeline()
    for game_id in game_ids:
        p.hget('game:%s' % game_id, 'p1')
        p.hget('game:%s' % game_id, 'p2')
        p.hget('game:%s' % game_id, 'elodiff')
    games = []
    for game_id, (player1, player2, elodiff) in izip(game_ids, grouper(p.execute(), 3)):
        print player1, player2, elodiff, game_id
        elodiff = float(elodiff)
        if elodiff < 0:
            player1, player2 = player2, player1
            elodiff = -elodiff

        games.append(dict(
            player1 = player1,
            player2 = player2,
            elodiff = elodiff,
            game_id = game_id,
        ))
    return games

@app.route("/")
def index():
    p = redis.pipeline()
    p.zrange('scoreboard', 0, 40, withscores=True)
    p.lrange('games', -40, -1)
    p.llen('games')
    highscores, last_game_ids, num_games = p.execute()

    highscores = [(username, -score) for username, score in highscores]
    last_games = make_game_list(list(reversed(last_game_ids)))

    return render_template('index.jinja',
        highscore_first = 0,
        highscores = highscores,
        last_games = last_games,
        num_games = num_games,
    )

@app.route("/player/<username>")
def player(username):
    rank = redis.zrank('scoreboard', username)
    highscore_first = max(0, rank - 10)

    p = redis.pipeline()
    p.zrange('scoreboard', highscore_first, highscore_first + 20, withscores=True)
    p.lrange('player:%s:games' % username, -40, -1)
    p.llen('player:%s:games' % username)
    highscores, last_game_ids, num_games = p.execute()

    highscores = [(score_user, -score) for score_user, score in highscores]
    last_games = make_game_list(list(reversed(last_game_ids)))

    return render_template('player.jinja',
        rank = rank + 1,
        highscore_first = highscore_first,
        highscores = highscores,
        username = username,
        last_games = last_games,
        num_games = num_games,
    )

@app.route("/game/<game_id>")
def game(game_id):
    pass

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    app.run(host='0.0.0.0', port=8080, debug=True)



