import redis
import sys
import math
import re

r = redis.StrictRedis(host='localhost', port=6379, db=0)

r.flushdb()

print("size of db : %s" % r.dbsize())

filepath = str(sys.argv[1])

k = 0

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      
      if len(tweet) == 0 :
        print(k)
      key = tweet[0]

      tweet.pop(0)
      tweet = ['"%s"' % t for t in tweet]
      tweet = '%s' % ','.join(tweet)
      
      r.set(key,tweet)

      k = k + 1

print("size of db : %s" % r.dbsize())
