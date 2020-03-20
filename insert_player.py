import redis
import sys
import random
import string
import os


def randomStringDigits(stringLength=16):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


redis_url = os.environ.get('REDIS_URL') or 'localhost'
redis = redis.Redis(host=redis_url)
redis.ping()

username = sys.argv[1]
password = randomStringDigits()
redis.set("user:%s" % username, password)

print(f"inserted {username} {password}")
