"""Process hashtags

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import redis
import string
import numpy as np
import math
import community
import itertools
import os
from operator import itemgetter
import sys
from collections import Counter
import random

# redis connection
rt = redis.StrictRedis(host='localhost', port=6379, db=1)

# add to graph
def addToGraph(tid,uid,tags) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G

  # lower the hashtags and remove "ferguson", too common
  tags = [t.lower() for t in tags if t.lower() not in ["ferguson"]]

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


# initialize hashtag graph
G = nx.Graph()

# input tweets
filepath = str(sys.argv[1])

# counter
k = 0

# <hashtag,tweet id> dictionnary
ht2tweets = {}

# <hashtag,user id> dictionnary
ht2users = {}

# all users tweets counter
allu = Counter()

# iterate tweets
with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      # get the content
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      # get the hashtags
      hashtags = tweet[10].split(" ")
      if len(hashtags) > 0 and hashtags[0] != "" :
        # add to graph
        addToGraph(tweet[0],tweet[2],hashtags)
      k = k + 1


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

# reduce edges of G
G = reduceEdges(G,100)

# find communities
partition = community.best_partition(G)

# communities dictionnary
v = {}


for key, value in sorted(partition.iteritems()):
    v.setdefault(value, []).append(key)

vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:10]
v = dict(filter(lambda i:i[0] in vs, v.iteritems()))


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


i = 0
for k in cdic :
  i = i + 1
  out = "tcomm_%s" % i
  output = open(out,'a')
  print(len(cdic[k]))
  for w in cdic[k] :
    output.write("%s\n" % w[0])

deg = U.degree()
to_remove = [n for n in deg if deg[n] == 0]
U.remove_nodes_from(to_remove)

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

plt.savefig("graphusers.png",dpi=200)

plt.clf()

print("done")

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]

#drawing
size = float(len(set(partition.values())))

print("now create layout..")
kk = set([j for i in v.values() for j in i])
H = G.subgraph(kk)

pos = nx.spring_layout(H)

print("layout done !")

d = nx.degree(G)

pos = nx.spring_layout(G)
nx.draw(G,pos, linewidths=0, node_size = 20, with_labels = False, alpha = 0.4,font_size = 6, node_color='#cccccc', edge_color='#cccccc')

i = 0
for part in v :
    np = v[part]
    T = G.subgraph(np)
    ledges = T.edges()
    caption = " ".join(np[:10])
    nx.draw_networkx_nodes(T,pos,np, node_size=20, node_color = str(getColor(i)),linewidths=0, label=caption)
    nx.draw_networkx_edges(T,pos,edgelist=ledges,edge_color=str(getColor(i)))
    i = i + 1

plt.legend(prop={'size':6})
plt.savefig("graph.png",dpi=200)

