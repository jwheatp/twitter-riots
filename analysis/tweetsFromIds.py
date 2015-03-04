import redis
import sys
import math
import re
import glob

comm_path = str(sys.argv[2])
tweetspath = str(sys.argv[1])

twts = {}

i = 0

for filename in glob.glob(comm_path):
  i = i + 1
  ids = open(filename).readlines()
  ids = [id.strip() for id in ids]
  twts[i] = ids

k = 0

tweets = {}

with open(tweetspath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = tweet.strip()
      tweeta = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      tid = tweeta[0]
      for l in twts :
        if tid in twts[l] :
          if l not in tweets :
            tweets[l] = []
          tweets[l].append(tweet)

      k = k + 1

i = 0
for k in tweets :
  i = i + 1
  out = "ct_%s" % i
  output = open(out,'a')
  for w in tweets[k] :
    output.write("%s\n" % w)

