import sys
import re
import datetime
import math
from collections import Counter

filepath = str(sys.argv[1])

counter = Counter()

k = 0

def hasakeytag(tags) :
  for tag in tags :
    if tag in keytags :
      return True
  return False

def hasakeyword(text) :
  for keyw in keywords :
    if keyw in text :
      return True
  return False

time = []
keywords = []
keytags = []
totalt = 0
i = 0
for ar in sys.argv :
  i = i + 1
  if ar == "-h" :
    time.append(sys.argv[i])
    time.append(sys.argv[i+1])
  if ar == "-k" :
    nk = int(sys.argv[i])
    for o in range(1,nk+1) :
      keywords.append(str(sys.argv[i+o]))
  if ar == "-t" :
    tt = int(sys.argv[i])
    for o in range(1,tt+1) :
      keytags.append(str(sys.argv[i+o]))

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      tokens = tweet[10].split(" ")
      tokens = [x.lower() for x in tokens if x.lower() != "ferguson" and x != '']

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) > 0 :
        dfrom = datetime.datetime.strptime(time[0], '%H:%M')
        dfrom = datetime.time(dfrom.hour,dfrom.minute)

        dto = datetime.datetime.strptime(time[1], '%H:%M')
        dto = datetime.time(dto.hour,dto.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        if len(keywords) == 0 or len(keywords) > 0 and hasakeyword(tweet[3]) :
          if len(keytags) == 0 or hasakeytag(tweet[10].split(" ")) :
            totalt = totalt + 1
            for tok in tokens :
              counter[tok] += 1
      k = k + 1

print("%s tweets found for the query" % totalt)

ht = counter.most_common(400)
ht = [x[0] for x in ht]
print(counter.most_common(50))    
