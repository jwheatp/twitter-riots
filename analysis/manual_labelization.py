import sys
from collections import Counter
import math
import datetime
import re
import numpy as np

filepath = str(sys.argv[1])
output = str(sys.argv[2])

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
with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        rt = re.findall(r"RT @([a-zA-Z0-9-_]*): (.*)",tweet[3])
        if len(rt) == 0 :
          print(tweet[3])

          label1 = raw_input("informative? \n")
          if label1 == 'y' :
            label1 = 1
          elif label1 == 'n' :
            label1 = 0

          label2 = raw_input("involved? \n")
          if label2 == 'y' :
            label2 = 1
          elif label2 == 'n' :
            label2 = 0

          outline = '%s,"%s","%s"\n' % (tweet[0],label1,label2)
          out = open(output,'a')
          out.write(outline)
          out.close()
          print(" ")
      k = k + 1

