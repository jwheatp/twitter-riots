import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
import datetime
import sys
from collections import Counter
import math
import re
import numpy as np

months = HourLocator()
hourFmt = DateFormatter('%H')

filepath = str(sys.argv[1])

mtagged = Counter()
tagged = Counter()
untagged = Counter()
total = Counter()
rt = Counter()
k = 0
with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      td = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S').strftime('%H')
      tags = tweet[10].split(" ")
      tags = sorted([t.lower() for t in tags])
      if len(tags) == 0 or set(tags).issubset(set([''])) :
        untagged[str(td)] += 1
      if set(tags).issubset(set(['ferguson','mikebrown'])) :
        mtagged[str(td)] += 1
      else :
        tagged[str(td)] += 1
      if int(tweet[8]) == 1 :
        rt[str(td)] += 1
      total[str(td)] += 1
      k = k + 1

tv = sorted([datetime.datetime.strptime(str(t),'%H') for t in tagged])


def process(serie) :
  serie = sorted(serie.items(), key=lambda k: int(k[0]))
  return [t[1] for t in serie]

counts_t = process(tagged)
counts_m = process(mtagged)
counts_u = process(untagged)
total = process(total)
rt = process(rt)

plt.plot_date(tv,counts_t,'-',label="tagged")
plt.plot_date(tv,counts_m,'-', label="min tagged")
plt.plot_date(tv,counts_u,'-',label="no tagged")
plt.plot_date(tv,total,'--',label="total")
plt.plot_date(tv,rt,'--',label="retweet")
plt.legend()
plt.gcf().autofmt_xdate()
plt.savefig(str(sys.argv[2]),dpi=200)