import redis
import community
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import math
import sys
import itertools
import random
from operator import itemgetter

def addToGraph(tags,user) :
  global G, keywords

  tags = [t.lower() for t in tags]

  username = user[1].lower()
  G.add_node(username)

  for tag in tags :
    if rt.exists(tag) :
      G.add_node(tag)
      if G.has_edge(username, tag) :
        G[username][tag]['weight'] += 1
      else :
        G.add_edge(username, tag, weight=1)

G = nx.Graph()

filepath = str(sys.argv[1])
output = str(sys.argv[2])

r = redis.StrictRedis(host='localhost', port=6379, db=0)
rt = redis.StrictRedis(host='localhost', port=6379, db=1)
k = 0

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
      mentions = tweet[11].split(",")
      if len(mentions) > 0 and mentions[0] != "" :
        user = r.get(tweet[2])
        if user != None :
          user = re.findall('"((?:(?!(?:",")).)*)"',r.get(tweet[2]))
          addToGraph(mentions,user)
      k = k + 1


#print("iteration done..")

#def getColor() :
#  r = lambda: random.randint(0,255)
#  return '#%02X%02X%02X' % (r(),r(),r())

#first compute the best partition
partition = community.best_partition(G)

v = {}

for key, value in sorted(partition.iteritems()):
    v.setdefault(value, []).append(key)

vs = sorted(v, key=lambda k: len(v[k]), reverse=True)[:10]
v = dict(filter(lambda i:i[0] in vs, v.iteritems()))
for key in v :
  degrees = nx.degree(G,set(v[key]))
  degrees = sorted(degrees, key=degrees.get, reverse=True)[:100]
  v[key] = degrees


i = 0
for k in v :
  i = i + 1
  out = "comm_%s" % i
  print(out)
  output = open(out,'a')
  for w in v[k] :
    output.write("%s\n" % rt.get(w))

#drawing
#size = float(len(set(partition.values())))

#print("now create layout..")
#kk = set([j for i in v.values() for j in i])
#H = G.subgraph(kk)

#pos = nx.spring_layout(H)
#pos = nx.graphviz_layout(H,"sfdp")

#print("layout done !")

#d = nx.degree(G)

#edges = sorted(H.edges(data = True), key = lambda (a, b, dct): dct['weight'],reverse=True)[:100]

#for part in v :
#    nx.draw_networkx_nodes(H,pos,v[part], node_size=[o*2 for o in d.values()], node_color = str(getColor()),linewidths=0)

#nx.draw_networkx_edges(H,pos,edgelist=edges, alpha=0.2)

#plt.savefig("graph.png",dpi=200)
