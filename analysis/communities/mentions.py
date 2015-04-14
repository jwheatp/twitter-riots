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

# add to graph
def addToGraph(tid,uid,tags) :
  """Process tweet to add his hashtags and user to the graphs
  :param tid : tweet id
  :param uid : user id
  :param tags : hashtags list
  """
  global G,found
  
  if len(tags) == 0 or len(tags) == 1 and tags[0] == '' :
    return
  user = r.get(int(uid))
 
  if user == None :
    return

  user = re.findall('"((?:(?!(?:",")).)*)"', user)
  
  # lower the hashtags
  tags = [t.lower() for t in tags]
  
  usern = user[1].lower()
  G.add_node(usern)

  found = found + 1

  if "-tfidf" in sys.argv :
    userId = tweet[2]
    words = tweet[3].split(",")
    ht = tweet[10].split(" ")
    ht = [h.lower() for h in ht if h not in [""]]
    mentions = tweet[11].split(",")
    mentions = [m.lower() for m in mentions if m not in [""]]
    words = [w for w in words if w not in ["amp","ferguson",""] and not w.isdigit()]
    if len(words) > 0 :
      if userId not in user2tweets :
        user2tweets[userId] = [0,Counter(),Counter(),Counter()]
      
      user2tweets[userId][0] = user2tweets[userId][0]+1
      user2tweets[userId][1].update(Counter(words))
      user2tweets[userId][2].update(Counter(ht))
      user2tweets[userId][3].update(Counter(mentions))

      allTweetsCounter.update(Counter(Counter(words).keys()))
      allHtagsCounter.update(Counter(Counter(ht).keys()))
      allMentionsCounter.update(Counter(Counter(mentions).keys()))

  # iterate through hashtags
  for tag in tags :
    # add hashtag to graph
    G.add_node(tag)
 
    #if not rt.get(tag) :
    #  return
    # update edge weight for every hashtag 2-permutation of the tweet
    if G.has_edge(usern,tag) :
      G[usern][tag]['weight'] += 1
    else :
      G.add_edge(usern, tag, weight=1)

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

if "-tfidf" in sys.argv :
  allTweetsCounter = Counter()
  allHtagsCounter = Counter()
  allMentionsCounter = Counter()
  user2tweets = {}

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
        # get the hashtags
        hashtags = tweet[11].split(",")
        # add to graph
        addToGraph(tweet[0],tweet[2],hashtags)
      
      k = k + 1


print("tweets found : %s over %s (%s without time consideration)" % (found,totalt,k))

sg = G

v = {}

param = int(sys.argv[3])

if "-automatic" in sys.argv :

  # keep the n more 
  tokeep = sorted(G.in_degree_iter(weight='weight'),key=itemgetter(1),reverse=True)[:param]
  tokeep = [t[0] for t in tokeep]

  G = G.subgraph(tokeep)

  # find communities
  partition = community.best_partition(G.to_undirected())
  for key, value in sorted(partition.iteritems()):
    v.setdefault(value, []).append(key)

if "-tfidf" in sys.argv :

  # find communities
  v = clusters.clusterize(user2tweets, allTweetsCounter, allHtagsCounter, allMentionsCounter)

if "-supervised" in sys.argv :
    # keep the n more 
  tokeep = sorted(G.in_degree_iter(weight='weight'),key=itemgetter(1),reverse=True)[:param]
  tokeep = [t[0] for t in tokeep]

  G = G.subgraph(tokeep)

  plabels = open("uclusters_11_08_02_04").readlines()
  l = 0
  labels = {}
  for l in plabels :
    kv = l.strip().split(",")
    uid = kv[0]
    name =  r.get(int(uid))
    if name == None :
      continue
    name = name.split(",")[1][1:-1].lower()
    if name in G.nodes() :
      labels[name] = kv[1]
  
  for key, value in sorted(labels.iteritems()):
    v.setdefault(value, []).append(key)

setofnodes = set()
for part in v :
    setofnodes = setofnodes | set(v[part])

G = G.subgraph(list(setofnodes))

commN = int(sys.argv[4])
vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:commN]
v = dict(filter(lambda i:i[0] in vs, v.iteritems()))

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]
  #r = lambda: random.randint(0,255)
  #return('#%02X%02X%02X' % (r(),r(),r()))

print("now create layout..")

d = sg.in_degree(G.nodes()).items()
d = sorted(d,key = lambda e : e[1],reverse=True)

gdeg = G.degree()
to_remove = [n for n in gdeg if gdeg[n] == 0]
G.remove_nodes_from(to_remove)

pos = nx.graphviz_layout(G,prog="sfdp")

print("layout done !")

node_size=[nn[1] * 1 for nn in d]

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
    caption = " ".join(np[:10])
    
    d = T.in_degree().items()
    d = sorted(d,key = lambda e : e[1],reverse=True)
    node_size=[ee[1] for ee in d]

    nx.draw_networkx_nodes(T,pos,np, node_size=1, node_color = str(getColor(i)),linewidths=0, label=caption, with_labels=True,font_size=6)
    nx.draw_networkx_edges(T,pos,edgelist=ledges,edge_color=str(getColor(i)),arrows=True,alpha=0.4)
    #edge_labels=dict([((uu,vv,),dd['weight']) for uu,vv,dd in T.edges(data=True)])
    #nx.draw_networkx_edge_labels(T,pos,edge_labels=edge_labels,color=str(getColor(i)))
    i = i + 1

#nx.draw_networkx_labels(G,pos,labels,font_size=6)

plt.legend(prop={'size':6})
plt.savefig("graph.png",dpi=200)

###################################################

if "-complete" in sys.argv :

  top_rt = open(str(sys.argv[2])).readlines()
  top_rt = [l.strip() for l in top_rt]
  top_rt = [re.findall('"((?:(?!(?:",")).)*)"', t) for t in top_rt]

  rts = {}

  print("---")

  k = 0
  for i in v :
    rts[k] = []
    for u in v[i] :
      uid = rt.get(u.lower())
      if uid != None :
        for tw in top_rt :
          if tw[2] == str(uid) :
            rts[k].append(tw)
    rts[k].sort(key=lambda x: int(x[4]), reverse=True)
    rts[k] = rts[k][:100]
    print("top tweets")
    print("---------------")
    for tt in rts[k][:10] :
      print(tt)
    print("random sample")
    print("---------------")
    print("----------------")
    print("----------------")
    k = k + 1

  correlations(rts)
