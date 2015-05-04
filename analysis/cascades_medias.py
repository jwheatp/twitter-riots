"""Process Cascades

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import datetime
import redis
import string
import numpy as np
import math
import Image
import community
import itertools
import os
from operator import itemgetter
import sys
from collections import Counter
import random
from correlations import correlations
import clusters

# add to graph
def process(current,rtlist) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global graphs,found

  orig = rtlist[-1]

  rtlist.append(current)

  if orig not in graphs :
    graphs[orig] = nx.Graph()

  for node in rtlist :
    graphs[orig].add_node(node)

  for i in range(len(rtlist)-1):
    graphs[orig].add_edge(rtlist[i], rtlist[i+1])

# redis connection
rtc = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0


# graph table
graphs = {}
tweets = {}

# input tweets
filepath = str(sys.argv[1])

# check time window
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


topusers = open("../../../data/users/users_fw_11_08_10msg+").readlines()
topusers = set([u.strip().split(",")[1] for u in topusers])

def username2id(id) :
  user = r.get(tweet[2])
  if user == None :
    return None
  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  user = user[1].lower()
  return user

rtclusters = {}

# counter
k = 0


topusers11 = ["michaelskolnik","antoniofrench","pzfeed","pdpj","youranonnews","khaledbeydoun","womenonthemove1"]

# iterate tweets
with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)

      # get the content
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      # parse date
      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      # if the time is good
      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :

        uname = username2id(tweet[2])
        current = (uname,len(tweets))
        tweets[(uname,tweet[3])] = current

        # check if it is an RT
        rtlist = []
        rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",tweet[3])

        while len(rt) > 0 :
          rt = rt[0]

          rtname = rt[0]
          mess = rt[1]

          if (rtname.lower(),mess) not in tweets :
            tweets[(rtname.lower(),mess)] = (rtname.lower(),len(tweets))
          rtlist.append(tweets[(rtname.lower(),mess)])

          rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",mess)

        if len(rtlist) > 0 :
          # add to graph
          if tweet[2] in topusers and rtlist[0][0] in topusers11 :
            if rtlist[0][0] not in rtclusters :
              rtclusters[rtlist[0][0]] = []
            rtclusters[rtlist[0][0]].append(uname)
          process(current,rtlist)
          found += 1

      k = k + 1

for c in rtclusters :
  rtclusters[c] = set(rtclusters[c])

def distJ(a,b) :
  return float(len(a & b)) / len(a | b)

distM = []

for u,i in zip(topusers11,range(len(topusers11))) :
  tmp = []
  for v,j in zip(topusers11,range(len(topusers11))) :
    dd = distJ(rtclusters[u],rtclusters[v])
    print(u)
    print(v)
    print(dd)
    tmp.append(dd)
  distM.append(tmp)

distM = np.array(distM)

print(distM)

#plt.clf()
#plt.figure(figsize=[7,7])
#plt.pcolor(distM,cmap=plt.cm.Blues)
#plt.colorbar(orientation='vertical')
#plt.savefig("heatmap11.png",dpi = 200)

graphs = sorted(graphs.items(), key=lambda x: len(x[1].nodes()), reverse = True)

if "-draw" in sys.argv :
  #for g in graphs[:100] :
    #print("%s : %s" %(g[0],len(g[1].nodes())))
  tweets = {v: k for k, v in tweets.items()}
  #graphs = graphs[:10]
  #print([tuple(tweets[g[0]]) for g in graphs])
  #G = nx.union_all([u[1] for u in graphs])
  print(tweets[graphs[0][0]])
  G = graphs[0][1]
  print("now create layout..")
  pos = nx.graphviz_layout(G,prog="sfdp")
  nx.draw(G,pos, linewidths=0, node_size = 5, with_labels = False, alpha = 0.5,font_size = 6, node_color='#862B59', edge_color='#cccccc',arrows=True)
  plt.legend(prop={'size':6})
  plt.savefig("graph.png",dpi=200)

if "-counter" in sys.argv :

  counter = Counter()

  for g in graphs[:100] :
    uname = g[0][0]
    counter[uname] += 1

  print(counter)

  vals = Counter([v[1] for v in counter.most_common()]).most_common()

  vals = sorted(vals,key=itemgetter(0), reverse=True)

  x = [v[1] for v in vals]
  y = [v[0] for v in vals]

  plt.clf()
  plt.figure(figsize=[7,7])
  plt.plot(x,y,'-o')
  plt.xlabel('number of users')
  plt.ylabel('number of tweets')
  plt.suptitle('User frequencies in the top 100 retweets')
  plt.savefig("freqInfluentUsers.png",dpi = 200)
