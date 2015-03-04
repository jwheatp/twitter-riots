import sys
import re
import math

filepath = str(sys.argv[1])
output = str(sys.argv[2])
k = 0

words = []

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      tokens = tweet[3].split(",")
      tokens = [x for x in tokens if x != "ferguson"]
      words.extend(tokens)
      k = k + 1

output = open(output,"a")
for item in words:
  output.write("%s\n" % item)
