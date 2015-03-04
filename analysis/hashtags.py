import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
import redis
import math
import community
import itertools
from operator import itemgetter
import sys
from collections import Counter
import random

rt = redis.StrictRedis(host='localhost', port=6379, db=1)

def addToGraph(tid,tags) :
  global G, keywords

  tags = [t.lower() for t in tags if t.lower() not in ["ferguson","mikebrown"]]

  for tag in tags :
    if tag not in ht2tweets :
      ht2tweets[tag] = Counter()
    ht2tweets[tag][tid] += 1
    G.add_node(tag.lower())

  for perms in itertools.permutations(tags,2) :
    a = perms[0]
    b = perms[1]
    if G.has_edge(a, b) :
      G[a][b]['weight'] += 1
    else :
      G.add_edge(a, b, weight=1)

#tophtpath = str(sys.argv[2])

#topht = open(tophtpath).readlines()
#topht = [ht.strip() for ht in topht]

G = nx.Graph()

filepath = str(sys.argv[1])

k = 0

ht2tweets = {}

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      hashtags = tweet[10].split(" ")
      if len(hashtags) > 0 and hashtags[0] != "" :
        addToGraph(tweet[0],hashtags)
      k = k + 1

def reduceNodes(S,param) :
  degs = S.degree()
  tokeep = sorted(degs, key=degs.get, reverse=True)[:len(S.nodes())/param]
  return S.subgraph(tokeep)

def reduceEdges(S,param) :
  old_edges = S.edges()
  edges = sorted(S.edges(data = True), key = lambda (a, b, dct): dct['weight'],reverse=True)[:param]

  S.remove_edges_from(old_edges)
  S.add_edges_from(edges)

  deg = S.degree()
  to_remove = [n for n in deg if deg[n] == 0]
  S.remove_nodes_from(to_remove)
  return S

G = reduceEdges(G,300)
#G = reduceNodes(G,3)

partition = community.best_partition(G)

v = {}

for key, value in sorted(partition.iteritems()):
    v.setdefault(value, []).append(key)

vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:10]
v = dict(filter(lambda i:i[0] in vs, v.iteritems()))

#for key in v :
#  degrees = nx.degree(G,set(v[key]))
#  degrees = sorted(degrees, key=degrees.get, reverse=True)[:100]
#  v[key] = degrees


cdic = {}
i = 0
for key in v :
  i = i + 1
  cdic[i] = Counter()
  for tag in v[key] :
    cdic[i].update(ht2tweets[tag])
  cdic[i] = cdic[i].most_common(1000)


i = 0
for k in cdic :
  i = i + 1
  out = "tcomm_%s" % i
  output = open(out,'a')
  for w in cdic[k] :
    output.write("%s\n" % w[0])


def getColor(k) :
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]

#drawing
size = float(len(set(partition.values())))

print("now create layout..")
kk = set([j for i in v.values() for j in i])
H = G.subgraph(kk)

pos = nx.spring_layout(H)
#pos = nx.graphviz_layout(H,"sfdp")

print("layout done !")

d = nx.degree(G)

#G,edges,to_remove = reduceEdges(G,1000)

#print(len(G.nodes()))
#print(G.nodes())
pos = nx.spring_layout(G)
nx.draw(G,pos, linewidths=0, node_size = 20, with_labels = False, alpha = 0.4,font_size = 6, node_color='#cccccc', edge_color='#cccccc')

#print(len(v))
i = 0
for part in v :
    np = v[part]
#    np = [x for x in v[part] if x not in to_remove]
#    T = G.subgraph(np)
#    T = reduceNodes(T,2)
#    T,ledges,lremove = reduceEdges(T,1000)
#    np = T.nodes()
#    np = [x for x in np if x not in lremove]
    T = G.subgraph(np)
    ledges = T.edges()
    caption = " ".join(np[:10])
    nx.draw_networkx_nodes(T,pos,np, node_size=20, node_color = str(getColor(i)),linewidths=0, label=caption)
    nx.draw_networkx_edges(T,pos,edgelist=ledges,edge_color=str(getColor(i)))
    #for comb in itertools.combinations(np,2) :
    #  a = comb[0]
    #  b = comb[1]
    #  existingEdges = []
    #  if T.has_edge(a,b) :
    #    existingEdges.append((a,b))
    #  nx.draw_networkx_edges(T,pos,edgelist=existingEdges,edge_color=str(getColor(i)))
    i = i + 1

#labels=dict((n,n) for n in H)
#nx.draw_networkx_labels(H,pos,labels,font_size=6)

#nx.draw_networkx_edges(H,pos,edgelist=edges, alpha=0.2)

plt.legend(prop={'size':6})
plt.savefig("graph.png",dpi=200)

