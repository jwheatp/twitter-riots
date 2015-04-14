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
def addToGraph(uid,rtname,omessage) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G,found
  
  # lower the rt username
  rtname = rtname.lower()

  # get tweet author infos from redis
  user = r.get(int(uid))
  #rttest = rtc.get(rtname)
 
  # if not in database, quit
  if user == None :
    return

  # read fields and take lower username
  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  user = user[1].lower()
  
  if user not in labels or rtname not in labels :
    return

  #if labels[user] == '0' or labels[rtname] == '0' :
  #  return

  twtCtn[user] += 1

  # add author and rtname to graph nodes
  G.add_node(user)
  G.add_node(rtname)

  # create edge or update weights
  if G.has_edge(rtname,user) :
    G[rtname][user]['weight'] += 1
  else :
    G.add_edge(rtname, user, weight=1)

# redis connection
rtc = redis.StrictRedis(host='localhost', port=6379, db=1)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

found = 0
totalt = 0

twtCtn = Counter()
users2tweets = {}

# initialize hashtag graph
G = nx.DiGraph()

if "-classify" in sys.argv :
    # keep the n more 
  #tokeep = sorted(G.in_degree_iter(weight='weight'),key=itemgetter(1),reverse=True)[:param]
  #tokeep = [t[0] for t in tokeep]

  #G = G.subgraph(tokeep)

  # get labels
  plabels = open("../scu_11_02_04").readlines()
  l = 0
  labels = {}
  for l in plabels :
    kv = l.strip().split(",")
    uid = kv[0]
    name =  r.get(int(uid))
    if name == None :
      continue
    name = name.split(",")[1][1:-1].lower()
    labels[name] = kv[1]
 
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
        rt = re.findall(r"RT @([a-zA-Z0-9-_]*):? (.*)",tweet[3])
        if len(rt) > 0 :
          rt = rt[0]
          found += 1
          # add to graph
          addToGraph(tweet[2],rt[0],rt[1])
      
      k = k + 1

# number of results considering the time window
print("%s results." % found)

sg = G

twtCtn = Counter(el for el in twtCtn.elements() if twtCtn[el] >= 4)
G = G.subgraph(twtCtn.keys())

# for each node keep the most influent predecessor
for node in G.nodes() :
  allnodes = G.predecessors(node)

  edges = G.in_edges([node],data=True)
  first = set()
  if len(edges) > 0 :
    edges = sorted(edges, key = lambda e : e[2]['weight'])
    first = set([edges[0][0]])
  toremove = set(allnodes) - first
  toremove = [(t,node) for t in toremove]
  G.remove_edges_from(toremove)

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#CCCCCC","#862B59","#0A6308","#A10000","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536"]
  return colors[k]

print("now create layout..")

UG = G.to_undirected()#
# extract subgraphs
sub_graphs = nx.connected_component_subgraphs(UG)

subs = []
for i, sg in enumerate(sub_graphs):
    subs.append((sg.nodes()))

subs.sort(key = lambda s: len(s), reverse=True)
fg = subs[0]

G = G.subgraph(fg)

###########

#gdeg = G.degree()
#to_remove = [n for n in gdeg if gdeg[n] == 0]
#G.remove_nodes_from(to_remove)

pos = nx.graphviz_layout(G,prog="sfdp")

print("layout done !")

########

centers = nx.pagerank(G)
centers = sorted(list(centers),key=itemgetter(1),reverse=True)[:20]

########

#centers = nx.out_degree_centrality(G)
#centers = sorted(centers,key=itemgetter(1),reverse=True)[:20]

colors = []
for node in G.nodes() :
  colors.append(getColor(int(labels[node])))

clabels = {}
for x in centers :
  clabels[str(x)] = str(x)

print(centers)

########

nx.draw(G,pos, linewidths=0, node_size = 5, with_labels = False, alpha = 0.5,font_size = 6, node_color=colors, edge_color='#cccccc',arrows=True)

nx.draw_networkx_labels(G,pos,clabels,font_size=6)

plt.legend(prop={'size':6})
plt.savefig("graph.png",dpi=200)
