import sys
import re
import datetime
from twarc import Twarc
import json
import csv
import os
import math
from collections import Counter
import random

filepath = str(sys.argv[1])

k = 0

count = 0

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

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      k = k + 1

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        count += 1

print("count : %s" % count)