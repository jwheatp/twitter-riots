"""Tweets to dictionary

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import sys
import math
import re
import datetime
from gensim import *
from collections import Counter

filepath = str(sys.argv[1])

allWords = Counter()

time = []
i = 0
for ar in sys.argv :
  i = i + 1
  if ar == "-h" :
    time.append(sys.argv[i])
    time.append(sys.argv[i+1])


if len(time) > 0 :
  dfrom = datetime.datetime.strptime(time[0], '%H:%M')
  dfrom = datetime.time(dfrom.hour,dfrom.minute)

  dto = datetime.datetime.strptime(time[1], '%H:%M')
  dto = datetime.time(dto.hour,dto.minute)

k = 0
# iterate tweets
with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      # get the content
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        tid = tweet[2]
        if "-medias" in sys.argv :
          tokens = re.findall('"((?:(?!(?:" ")).)*)"', tweet[12])
          tokens.extend(re.findall('"((?:(?!(?:",")).)*)"', tweet[13]))
        else :
          tokens = tweet[3].split(",")
          tokens = [w for w in words if w not in ["amp","ferguson",""] and not w.isdigit()]
        if len(tokens) > 0 :
          allWords.update(tokens)
      k = k + 1

allWords = Counter(el for el in allWords.elements() if allWords[el] >= 800)

print(allWords)

f = open("medias_11_08_100", "w")
for w in allWords.most_common() :
  f.write("%s\n" % w[0])
f.close()
