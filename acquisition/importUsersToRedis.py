"""Import users content to redis database

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import redis
import sys
import math
import re

# connect to redis database
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# drop db content
r.flushdb()

print("size of db : %s" % r.dbsize())

# input file of users
filepath = str(sys.argv[1])

# counter
k = 0

# iterate through users 
with open(filepath) as f:
    for user in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      user = re.findall('"((?:(?!(?:",")).)*)"', user)
      
      if len(user) == 0 :
        print(k)
      key = user[0]

      user.pop(0)
      user = ['"%s"' % t for t in user]
      user = '%s' % ','.join(user)
      
      r.set(key,user)

      k = k + 1

print("size of db : %s" % r.dbsize())
