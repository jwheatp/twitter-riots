import redis
import sys
import math
import re

r = redis.StrictRedis(host='localhost', port=6379, db=1)

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
      key = tweet[2].lower()
      value = tweet[0] 

      r.set(key,value)

      k = k + 1

print("size of db : %s" % r.dbsize())
