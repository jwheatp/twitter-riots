"""Import users names and ids to redis database

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import redis
import sys
import math
import re

# connect to redis database
r = redis.StrictRedis(host='localhost', port=6379, db=1)

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

      # extract fields
      user = re.findall('"((?:(?!(?:",")).)*)"', user)
      
      if len(user) == 0 :
        print(k)

      # the key is the username
      key = user[2].lower()

      # the value is the id
      value = user[0] 
      
      # insert
      r.set(key,value)

      k = k + 1

print("size of db : %s" % r.dbsize())
