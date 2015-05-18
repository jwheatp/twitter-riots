"""Process mentions

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

# redis connection
rt = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]

# add to graph
def addToGraph(tid,uid,mentions) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G,found

  user = r.get(int(uid))
 
  if user == None :
    return

  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  
  # lower the hashtags
  mentions = [t.lower() for t in mentions if t not in [""]]
  
  usern = user[1].lower()

  G.add_node(usern)

  found = found + 1

  # iterate through mentions
  for m in mentions :
    # add hashtag to graph
    G.add_node(m)
 
    # update edge weight for every hashtag 2-permutation of the tweet
    if G.has_edge(usern,m) :
      G[usern][m]['weight'] += 1
    else :
      G.add_edge(usern,m,weight=1)

# initialize hashtag graph
G = nx.DiGraph()

# input tweets
filepath = str(sys.argv[1])

time = []
keywords = []
keytags = []
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

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        totalt = totalt + 1
        # get the mentions
        mentions = tweet[11].split(",")
        if tweet[8] == '1' :
          continue
        # add to graph
        if len(mentions) > 0 and mentions[0] != "" :
          addToGraph(tweet[0],tweet[2],mentions)
      
      k = k + 1


print("tweets found : %s over %s (%s without time consideration)" % (found,totalt,k))

v = {}

# keep the n more 
tokeep = sorted(G.in_degree_iter(weight='weight'),key=itemgetter(1),reverse=True)[:500]
tokeep = [t[0] for t in tokeep]
G = G.subgraph(tokeep)

UG = G.to_undirected()#
#extract subgraphs
sub_graphs = nx.connected_component_subgraphs(UG)

subs = []
for i, sg in enumerate(sub_graphs):
    subs.append((sg.nodes()))

subs.sort(key = lambda s: len(s), reverse=True)

G = G.subgraph(subs[0])

# find communities
partition = community.best_partition(G.to_undirected())
for key, value in sorted(partition.iteritems()):
  v.setdefault(value, []).append(key)

setofnodes = set()
for part in v :
    setofnodes = setofnodes | set(v[part])
#G = G.subgraph(list(setofnodes))

vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:3]
v = dict(filter(lambda i:i[0] in vs, v.iteritems()))

print("now create layout..")

pos = nx.graphviz_layout(G,prog="sfdp")

print("layout done !")

#node_size=[nn[1] * 1 for nn in G.degree()]

labels = {}
###################################
for x in G.nodes() :
  labels[str(x)] = str(x)

##################################

nx.draw(G,pos, linewidths=0, node_size = 1, with_labels = False, alpha = 0.5,font_size = 6, node_color='#ED7E66', edge_color='#cccccc',arrows=True)

i = 0

for part in v :
    np = [n for n in v[part] if n in G.nodes()]
    T = G.subgraph(np)
    for x in T.nodes() :
      labels[str(x)] = str(x)

    ledges = T.edges()
    
    d = T.in_degree().items()
    d = sorted(d,key = lambda e : e[1],reverse=True)
    node_size=[ee[1] for ee in d]

    nx.draw_networkx_nodes(T,pos,np, node_size=1, node_color = str(getColor(i)),linewidths=0, font_size=6)
    nx.draw_networkx_edges(T,pos,edgelist=ledges,edge_color=str(getColor(i)),arrows=True,alpha=0.4)

    i = i + 1

plt.savefig("graph.png",dpi=200)

