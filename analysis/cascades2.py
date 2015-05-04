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
  global G,found

  orig = rtlist[-1]

  rtlist.append(current)

  for node in rtlist :
    G.add_node(node)

  for i in range(len(rtlist)-1):
    G.add_edge(rtlist[i], rtlist[i+1])

# redis connection
rtc = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0


G = nx.Graph()

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
topusers = set([u.strip().split(",")[1] for u in topusers[:50]])

def username2id(id) :
  user = r.get(tweet[2])
  if user == None :
    return None
  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  user = user[1].lower()
  return user

# counter
k = 0

tweets = {}

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
      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto and tweet[2] in topusers :

        uname = username2id(tweet[2])
        #current = (uname,len(tweets))
        current = uname
        tweets[(uname,tweet[3])] = current

        # check if it is an RT
        rtlist = []
        rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",tweet[3])

        if len(rt) > 0 :
          rt = rt[0]

          rtname = rt[0]
          mess = rt[1]

          #if (rtname.lower(),mess) not in tweets :
            #tweets[(rtname.lower(),mess)] = (rtname.lower(),len(tweets))
          #rtlist.append(tweets[(rtname.lower(),mess)])
          rtlist.append(rtname.lower())

          #rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",mess)

        if len(rtlist) > 0 :
          # add to graph

          process(current,rtlist)
          found += 1

      k = k + 1


if "-draw" in sys.argv :

  print(len(G.nodes()))


  UG = G.to_undirected()#
  #extract subgraphs
  sub_graphs = nx.connected_component_subgraphs(UG)

  subs = []
  for i, sg in enumerate(sub_graphs):
    subs.append((sg.nodes()))

  subs.sort(key = lambda s: len(s), reverse=True)
  fg = subs[0]

  G = G.subgraph(fg)
  
  centers = ["michaelskolnik","antoniofrench","pzfeed","pdpj","youranonnews","khaledbeydoun","womenonthemove1"]

  clabels = {}
  for x in centers :
    if x in G.nodes() :
      clabels[str(x)] = str(x)

  print("now create layout..")
  pos = nx.graphviz_layout(G,prog="sfdp")
  nx.draw(G,pos, linewidths=0, node_size = 5, with_labels = False, alpha = 0.5,font_size = 6, node_color='#862B59', edge_color='#cccccc',arrows=True)
  nx.draw_networkx_labels(G,pos,clabels,font_size=6)
  plt.legend(prop={'size':6})
  plt.savefig("graph.png",dpi=200)
