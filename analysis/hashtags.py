"""Process hashtags

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import colorConverter
import re
import datetime
import redis
import string
import numpy as np
import math
import community
import itertools
import argparse
import os
from operator import itemgetter
import sys
from collections import Counter
import random

##########################################
## Arguments
##########################################

parser = argparse.ArgumentParser(description='Generate hashtags graphs')

parser.add_argument('--filepath', dest='filepath',
                   help='path of the tweets file')

parser.add_argument('--output', dest='output', default="graph_hashtags.png",
                   help='graph output name')

parser.add_argument('--time', dest='time', nargs=2,
                   help='time window')

parser.add_argument('--rmtags', dest='rmtags', nargs='*',
                   help='remove tags')

parser.add_argument('--comms', dest='comms', type=bool, default=False,
                   help='search communities')

parser.add_argument('--allnodes', dest='allnodes', type=bool, default=False,
                   help='print all nodes')

parser.add_argument('--users', dest='users', type=bool, default=False,
                   help='compute user graph')

parser.add_argument('--usersOutput', dest='uOutput', default="graph_hashtags_users.png",
                   help='users graph output name')

args = parser.parse_args()

##########################################
## Functions
##########################################

# add to graph
def addToGraph(tid,uid,tags) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G,found

  # lower the hashtags and remove "ferguson", too common
  tags = [t.lower() for t in tags if t.lower() not in rmtags + [""]]

  if len(tags) > 0 :
    found = found + 1
    # iterate through hashtags
    for tag in tags :
      # make a <hashtag,tweet id> dictionnary
      if tag not in ht2tweets :
        ht2tweets[tag] = Counter()
      ht2tweets[tag][tid] += 1

      # make a <hashtag,user id> dictionnary
      if tag not in ht2users :
        ht2users[tag] = Counter()
      ht2users[tag][uid] += 1

      # add hashtag to graph
      G.add_node(tag.lower())

    # update edge weight for every hashtag 2-permutation of the tweet
    for perms in itertools.permutations(tags,2) :
      a = perms[0]
      b = perms[1]
      if G.has_edge(a, b) :
        G[a][b]['weight'] += 1
      else :
        G.add_edge(a, b, weight=1)

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  #colors = [(134,43,89,1),(161,0,0,1)]
  return colors[k]

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

def tronc(f) :
  return float("{0:.2f}".format(f))

# initialize hashtag graph
G = nx.Graph()

# redis connection
rt = redis.StrictRedis(host='localhost', port=6379, db=1)

# counters
found = 0
totalt = 0

time = []
rmtags = []

i = 0

if args.time != None :
  time = args.time

if args.rmtags != None :
  rmtags = args.rmtags

# counter
k = 0

# <hashtag,tweet id> dictionnary
ht2tweets = {}

# <hashtag,user id> dictionnary
ht2users = {}

# all users tweets counter
allu = Counter()

##########################################
## Acquisition
##########################################

# iterate tweets
with open(args.filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      # get the content
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) > 0 :
        dfrom = datetime.datetime.strptime(time[0], '%H:%M')
        dfrom = datetime.time(dfrom.hour,dfrom.minute)

        dto = datetime.datetime.strptime(time[1], '%H:%M')
        dto = datetime.time(dto.hour,dto.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        totalt = totalt + 1

        # get the hashtags
        hashtags = tweet[10].split(" ")
        if len(hashtags) > 0 and hashtags[0] != "" :
          # add to graph
          addToGraph(tweet[0],tweet[2],hashtags)

      k = k + 1


print("tweets found : %s over %s (%s without time consideration)" % (found,totalt,k))

##########################################
## Process
##########################################

# Hashtags processing
########################

# reduce edges of G
G = reduceEdges(G,500)

if args.comms :
  # find communities
  partition = community.best_partition(G)

  # communities dictionnary
  v = {}

  for key, value in sorted(partition.iteritems()):
      v.setdefault(value, []).append(key)

  vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:5]
  v = dict(filter(lambda i:i[0] in vs, v.iteritems()))

  #drawing
  size = float(len(set(partition.values())))

print("now create layout..")

d = nx.degree(G)

pos = nx.graphviz_layout(G,"neato")

ax = plt.figure(figsize=[7,7])
ax = plt.subplot(111)
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

print("layout done !")

if args.comms :
  if args.allnodes :
    nx.draw(G,pos, linewidths=0, node_size = 20, with_labels = False, alpha = 1,font_size = 6, node_color='#cccccc', edge_color='#cccccc')

  edgesValues = [G[p[0]][p[1]]['weight'] for p in G.edges()]
  maxEdgesValue = max(edgesValues)

  i = 0
  for part in v :
      np = v[part]
      T = G.subgraph(np)
      ledges = T.edges()

      ledgesOpa = [tronc(math.log(float(T[p[0]][p[1]]['weight']))/math.log(maxEdgesValue)) for p in ledges]

      ledgesColors = [colorConverter.to_rgba(str(getColor(i))) for e in ledges]
      ledgesColors = [tuple([c[0][0],c[0][1],c[0][2],c[1]]) for c in zip(ledgesColors,ledgesOpa)]

      caption = " ".join(np[:8])
      nx.draw_networkx_nodes(T,pos,np, node_size=20, node_color = str(getColor(i)),linewidths=0, label=caption)

      nx.draw_networkx_edges(T,pos,edgelist=ledges,edge_color=ledgesColors)
      i = i + 1

else :
  nx.draw(G,pos, linewidths=0, node_size = 20, with_labels = False, alpha = 1,font_size = 6, node_color=str(getColor(1)), edge_color=str(getColor(1)))

plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=1,prop={'size':8})
plt.savefig(args.output,dpi=200)

# Users processing
########################

if args.users :
  plt.clf()
  cdic = {}
  udic = {}

  alluset = set(allu.keys())


  U = nx.Graph()
  U.add_nodes_from(set(str(x) for x in range(10)))

  i = 0
  for key in v :
    i = i + 1
    cdic[i] = Counter()
    udic[i] = Counter()
    for tag in v[key] :
      cdic[i].update(ht2tweets[tag])
      utoadd = ht2users[tag]
      udic[i].update(utoadd)
    udic[i] = udic[i].most_common(1000)
    udic[i] = udic[i][:100]
    for user in udic[i] :
      for r in range(user[1]) : 
        allu[user[0]] += 1
    cdic[i] = cdic[i].most_common(1000)

  for i in udic :
    for user in udic[i] :
      we = float(user[1])/float(allu[user[0]])
      U.add_node(user[0])
      U.add_edge(str(i-1),user[0],weight=we)

  pos = nx.graphviz_layout(U,"neato")


  labels = {}
  for x in range(10) :
    if str(x) in U.nodes() :
      labels[str(x)] = str(x)

  sizes = []
  for n in U.nodes() :
    sizes.append(sum([item[2]["weight"] for item in U.edges(data=True) if n in item]))

  ecol = [U[p[0]][p[1]]['weight'] for p in U.edges()]
  nx.draw(U,pos,node_size=sizes,linewidths=0,alpha = 1, node_color='#E85858', edge_color=ecol,edge_cmap=plt.cm.Blues)
  nx.draw_networkx_labels(U,pos,labels,font_size=10)

  plt.savefig(args.uOutput,dpi=200)

  plt.clf()

  print("done")