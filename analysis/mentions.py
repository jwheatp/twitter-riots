import redis
import networkx as nx
import matplotlib.pyplot as plt
import re
import math
import sys
import itertools
from operator import itemgetter

def addToGraph(tags) :
  global G, keywords

  tags = [t.lower() for t in tags]

  for tag in tags :
    G.add_node(tag.lower())

  for perms in itertools.permutations(tags,2) :
    a = perms[0]
    b = perms[1]
    if G.has_edge(a, b) :
      G[a][b]['weight'] += 1
    else :
      G.add_edge(a, b, weight=1)

G = nx.Graph()

filepath = str(sys.argv[1])

r = redis.StrictRedis(host='localhost', port=6379, db=0)

k = 0

with open(filepath) as f:
    for tweet in f:
        if k < 1000000 :
          if math.fmod(k,100000) == 0 :
            print(k)
          tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)
          mentions = tweet[10].split(",")
          if len(mentions) > 0 and mentions[0] != "" :
            # addToGraph(mentions)
            print(tweet[2])
            print(r.get(tweet[2]))
          k = k + 1

top_edges_names = []

limit = 100

top_edges = sorted(G.edges(data = True), key = lambda (a, b, dct): dct['weight'],reverse=True)[:limit]

for a, b, dct in top_edges :
    top_edges_names.append((a,b))

T = nx.Graph(top_edges_names)

sizes = []
for n in T.nodes() :
  sizes.append(sum([item[2]["weight"]/10 for item in top_edges if n in item]))

dt = nx.degree(G)

colors=range(limit)
nx.draw(T, edges = T.edges(),edge_color=colors,width=2,edge_cmap=plt.cm.Reds, node_size=sizes, with_labels=True,alpha=0.2,weights = [G[p[0]][p[1]]['weight'] for p in top_edges_names],font_size=6)

plt.savefig("graph.pdf")
