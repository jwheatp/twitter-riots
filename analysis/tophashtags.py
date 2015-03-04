import sys
import re
import math
from collections import Counter

filepath = str(sys.argv[1])
output = str(sys.argv[2])

counter = Counter()

k = 0

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      tokens = tweet[10].split(" ")
      tokens = [x.lower() for x in tokens if x.lower() != "ferguson" and x != '']
      for tok in tokens :
        counter[tok] += 1
      k = k + 1

ht = counter.most_common(400)
ht = [x[0] for x in ht]
#print(counter.most_common(200))

output = open(output,"a")
for item in ht:
  output.write("%s\n" % item)     
