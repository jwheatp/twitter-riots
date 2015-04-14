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
def process(uid,rtname,mess) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global graphs,found
  
  # lower the rt username
  rtname = rtname.lower()

  # get tweet author infos from redis
  user = r.get(int(uid))
  #rttest = rtc.get(rtname)
 
  # if not in database, quit
  if user == None or rtc.get(rtname) == None :
    return

  # read fields and take lower username
  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  user = user[1].lower()

  if mess not in graphs :
    graphs[mess] = nx.Graph()

  # add author and rtname to graph nodes
  graphs[mess].add_node(user)
  graphs[mess].add_node(rtname)

  # create edge or update weights
  if graphs[mess].has_edge(rtname,user) :
    graphs[mess][rtname][user]['weight'] += 1
  else :
    graphs[mess].add_edge(rtname, user, weight=1)

# redis connection
rtc = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0


# graph table
graphs = {}

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


# counter
k = 0

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

        # check if it is an RT
        ulist = []
        rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",tweet[3])
        
        while len(rt) > 0 :
          rt = rt[0]

          rtname = rt[0]
          mess = rt[1]

          ulist.append(rtname)

          rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",mess)

        if len(ulist) > 0 :
          # add to graph
          #process(tweet[2],rtname,mess)
          found += 1
      
      k = k + 1

# number of results considering the time window
print("%s results." % found)

graphs = sorted(graphs.items(), key=lambda x: len(x[1].nodes()), reverse = True)


G = graphs[0]

print(G)

G = G[1]

print("now create layout..")

pos = nx.graphviz_layout(G,prog="sfdp")

nx.draw(G,pos, linewidths=0, node_size = 5, with_labels = False, alpha = 0.5,font_size = 6, node_color='#862B59', edge_color='#cccccc',arrows=True)

plt.legend(prop={'size':6})
plt.savefig("graph.png",dpi=200)
