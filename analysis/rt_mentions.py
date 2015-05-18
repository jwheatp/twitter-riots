"""Process RT mentions

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
import matplotlib.patheffects as PathEffects
import math
import pickle
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

def reduceEdges(S,param) :
  """Reduce edges, returns graph with top n edges
  :param S : graph
  :param param: number of edges to keep
  """
  # save old edges
  old_edges = S.edges()

  # take top edges
  edges = sorted(S.edges(data = True), key = lambda (a, b, dct): dct['weight'],reverse=True)[:param]

  # update graph edges
  S.remove_edges_from(old_edges)
  S.add_edges_from(edges)

  # clean graph by removing degree-0 nodes
  deg = S.degree()
  to_remove = [n for n in deg if deg[n] == 0]
  S.remove_nodes_from(to_remove)
  return S

def removeUnitEdges(S) :
  # save old edges
  old_edges = S.edges()

  # take top edges
  edges = [e for e in S.edges(data = True) if e[2]['weight'] <= 1]

  # update graph edges
  S.remove_edges_from(edges)

  return S

# add to graph
def addToGraph(uname,rtname) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G,found

  if rtname == '' :
    return

  # lower the rt username
  rtname = rtname.lower()

  user = uname

  twtCtn[user] += 1

  # add author and rtname to graph nodes
  G.add_node(user)
  G.add_node(rtname)

  # create edge or update weights
  if G.has_edge(user,rtname) :
    G[user][rtname]['weight'] += 1
  else :
    G.add_edge(user, rtname, weight=1)

# redis connection
rtc = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0

twtCtn = Counter()
users2tweets = {}

# initialize hashtag graph
G = nx.DiGraph()

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

polars = pickle.Unpickler(open("types_11", "r")).load()
knames = set(polars.keys())

for p in polars :
  if polars[p] < -0.5 :
    polars[p] = 1
  elif polars[p] >= -0.5 and polars[p] <= 0.5 :
    polars[p] = 2
  else :
    polars[p] = 3

print(Counter(polars.values()))

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

        if tweet[8] == '1' :

          # get tweet author infos from redis
          user = r.get(int(tweet[2]))
          # if not in database, quit
          if user == None :
            continue
          # read fields and take lower username
          user = re.findall('"((?:(?!(?:",")).)*)"', user)
          user = user[1].lower()

          rtname = tweet[11].split(',')[0]
          found += 1

          # add to graph
          addToGraph(user,rtname)

      k = k + 1

# number of results considering the time window
print("%s results." % len(G.nodes()))

#G = G.subgraph(knames)

polarsC1 = [n for n in polars if polars[n] == 1]
polarsC2 = [n for n in polars if polars[n] == 2]
polarsC3 = [n for n in polars if polars[n] == 3]

G1 = G.subgraph(polarsC1)
G2 = G.subgraph(polarsC2)
G3 = G.subgraph(polarsC3)

centers1 = nx.pagerank(G1)
centers1 = sorted(centers1.items(),key=itemgetter(1),reverse=True)
centers1 = [t[0] for t in centers1]
centers1 = centers1[:1000]

centers2 = nx.pagerank(G2)
centers2 = sorted(centers2.items(),key=itemgetter(1),reverse=True)
centers2 = [t[0] for t in centers2]
centers2 = centers2[:1000]

centers3 = nx.pagerank(G3)
centers3 = sorted(centers3.items(),key=itemgetter(1),reverse=True)
centers3 = [t[0] for t in centers3]
centers3 = centers3[:1000]

centers = set(centers1 + centers2 + centers3)

G = G.subgraph(centers)

if "-unit" in sys.argv :
  unitN = 1
  # for each node keep the most influent predecessor
  for node in G.nodes() :
    allnodes = G.successors(node)
    edges = G.out_edges([node],data=True)
    first = set()
    if len(edges) > 0 :
      edges = sorted(edges, key = lambda e : e[2]['weight'], reverse=True)
      first = set([e[1] for e in edges[:unitN]])
    toremove = set(allnodes) - first
    toremove = [(node,t) for t in toremove]
    G.remove_edges_from(toremove)

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7"]
  return colors[k]

def plotGraph(G,k) :
  print("now create layout..")

  print(len(G.nodes()))
  colors = [getColor(int(polars[n])) if n in polars else '#cccccc' for n in G.nodes()]

  pos = nx.graphviz_layout(G,prog="sfdp")

  print("layout done !")

  plt.clf()
  nx.draw(G,pos, linewidths=0, node_size = 10, with_labels = False, alpha = 0.6,font_size = 6, node_color=colors, edge_color="#cccccc",arrows=True)

  plt.legend(prop={'size':6})
  plt.savefig("graph_%s.png" % k,dpi=200)

UG = G.to_undirected()#
#extract subgraphs
sub_graphs = nx.connected_component_subgraphs(UG)

subs = []
for i, sg in enumerate(sub_graphs):
    subs.append((sg.nodes()))

subs.sort(key = lambda s: len(s), reverse=True)

for i in range(1) :
  fg = subs[i]
  plotGraph(G.subgraph(fg),i)
