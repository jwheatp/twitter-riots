import sys
import math
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nltk
import random
import urllib2
from collections import Counter
import datetime
import urlclean
from nltk.probability import FreqDist
import tsne
from operator import itemgetter
from sklearn import metrics
from sklearn.cluster import KMeans,DBSCAN
from sklearn.preprocessing import scale
import redis
import requests
from sklearn.preprocessing import StandardScaler
import networkx as nx
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
import matplotlib.patheffects as PathEffects
import itertools
import user_counts

labelspath = str(sys.argv[1])

labels = open(labelspath).readlines()
labels = dict(tuple(l.strip().split(',')) for l in labels)

mlabels = set([l[0] for l in labels.items() if l[1] == '2'])

print(mlabels)

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

G = nx.DiGraph()

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def addToGraph(user,rtname) :
  global G
  if user not in G.nodes() :
    G.add_node(user)
  if rtname not in G.nodes() :
    G.add_node(rtname)
  if G.has_edge(rtname,user) :
    G[rtname][user]['weight'] += 1
  else :
    G.add_edge(rtname, user,weight=1)

def bow2vec(words) :
  words = dict(words)
  return [words[x] if x in words else 0 for x in vocab]

vocab = open("medias_11_08_above100").readlines()
vocab = [v.strip() for v in vocab]

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

# input tweets
filepath = str(sys.argv[2])

tweets = {}

inv = set()

typeCounter = {}
users2infos = {}

k = 0
with_medias = 0
total_in_time = 0

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
        total_in_time += 1
        medias = re.findall('"((?:(?!(?:" ")).)*)"', tweet[12])
        medias.extend(re.findall('"((?:(?!(?:",")).)*)"', tweet[13]))

        if len(medias) > 0 :
          with_medias += 1

        for med in medias :
          if med in mlabels :
              user = r.get(int(tweet[2]))
              if user != None :
                user = re.findall('"((?:(?!(?:",")).)*)"', user)
                user = user[1].lower()
                rtname = tweet[11].split(",")[0].lower()
                if rtname != "" :
                  addToGraph(user,rtname)
                  inv.add(tweet[2])
                  break
        if "-countTypes" in sys.argv :
          for med in medias :
            if med in labels :
              user = r.get(int(tweet[2]))
              if user != None :
                user = re.findall('"((?:(?!(?:",")).)*)"', user)
                cnt_tweets = int(user[6])
                cnt_followers = int(user[7])
                cnt_friends = int(user[8])
                user = user[1].lower()
                users2infos[user] = tuple((cnt_tweets,cnt_followers,cnt_friends))
                if user not in typeCounter :
                  typeCounter[user] = Counter()
                typeCounter[user][labels[med]] += 1
                if int(tweet[8]) == 1 :
                  ment = tweet[11].split(",")[0].lower()
                  if ment not in typeCounter :
                    typeCounter[ment] = Counter()
                  typeCounter[ment][labels[med]] += 1
                  users2infos[ment] = tuple((-1,-1,-1))


        if "-tsne" in sys.argv :
          counts = Counter(medias).most_common()
          vec = bow2vec(counts)
          if sum(vec) > 0 :
            if tweet[2] not in tweets :
              tweets[tweet[2]] = [0] * len(vocab)
            tweets[tweet[2]] = [x + y for x, y in zip(vec, tweets[tweet[2]])]
      k = k + 1

print("%s tweets over %s has at least a media." %(with_medias, total_in_time))


# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

def tronc(f) :
  return float("{0:.2f}".format(f))

undefined = [name for name in users2infos if users2infos[name] == (-1,-1,-1)]
undefined_counts = user_counts.getCounts(undefined)
users2infos = dict(users2infos.items() + undefined_counts.items())

typeCounter = dict([el for el in typeCounter.items() if sum(el[1].values()) >= 3 and users2infos[el[0]] != (-1,-1,-1)])

for user in typeCounter :
  total = sum(typeCounter[user].values())
  vec = [0] * 3
  for v in typeCounter[user] :
   vec[int(v)] = tronc(float(typeCounter[user][v])/float(total))
  typeCounter[user] = vec

topusers = {'michaelskolnik': 25, 'antoniofrench': 12, 'pzfeed': 4, 'pdpj': 4, 'youranonnews': 3, 'khaledbeydoun': 1, 'womenonthemove1': 1, 'robertdedwards': 1, 'stlabubadu': 1, 'ericwolfson': 1, 'marmel': 1, 'ribriguy': 1, 'djwitz': 1, 'professorcrunk': 1, 'jasiri_x': 1, 'dtsteele': 1, 'dierdrelewis': 1, 'stevegiegerich': 1, 'holzmantweed': 1, 'stjamesstjames': 1, 'blistpundit': 1, 'thebloggess': 1, 'so_lo_travels': 1, 'coryprovost': 1, 'kerrywashington': 1, 'therealbanner': 1, '2chainzlyrics': 1, 'mmmphoenix': 1, 'kirbyoneal': 1, 'rolandsmartin': 1, 'peacebang': 1, 'negrointellect': 1, 'kiash__': 1, 'iamnatejames': 1, 'rt_com': 1, 'breakinthebank': 1, 'breakingnews': 1, 'auragasmic': 1, 'ksdknews': 1, 'so_treu': 1, 'brennamuncy': 1, 'sunnyhostin': 1, 'breevive': 1, 'theinventher': 1, 'mmgterrick24': 1, 'kirkman': 1, 'caseyjaldridge': 1, 'untoldmysteries': 1, 'syndicalisms': 1, 'marcusjulienlee': 1, 'shugnice': 1, 'politibunny': 1, 'lolitasaywhat': 1, 'chrislhayes': 1, 'locsofpassion': 1, 'moundcity': 1, 'lisabolekaja': 1}

output = open('users_medias_types_11','w')
output.write("name,tweets,followers,friends,garbage,informative,biased,influent\n")
for user in typeCounter :
  vec = typeCounter[user]
  if user in topusers :
    istopuser = "influent"
  else :
    istopuser = "non influent"
  output.write("%s,%s,%s,%s,%s,%s,%s,%s\n" %(user,users2infos[user][0],users2infos[user][1],users2infos[user][2],vec[0],vec[1],vec[2],istopuser))

output.close()

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

tweets = dict([t for t in tweets.items() if sum(t[1]) >= 5])

keys = tweets.keys()
tweets = tweets.values()

print(len(tweets))

if "-unit" in sys.argv :
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

UG = G.to_undirected()#
#extract subgraphs
sub_graphs = nx.connected_component_subgraphs(UG)

subs = []
for i, sg in enumerate(sub_graphs):
    subs.append((sg.nodes()))

subs.sort(key = lambda s: len(s), reverse=True)

fg = subs[:10]
fg = list(itertools.chain.from_iterable(fg))
G = G.subgraph(fg)

topnodes = sorted(G.degree_iter(),key=itemgetter(1),reverse=True)[:10]
topnodes = [t[0] for t in topnodes]
pos = nx.graphviz_layout(G, prog="sfdp")
ax = plt.gca()
for lb in topnodes :
  ltxt = "%s*" % lb
  lcol = "#C4272A"
  lsize = 8
  txt = ax.text(pos[lb][0], pos[lb][1], ltxt,fontsize=lsize, color=lcol, ha= 'center')
  txt.set_path_effects([PathEffects.Stroke(linewidth=2, alpha = 0.8, foreground="w"), PathEffects.Normal()])

#node_size=[d[v]*2+4 for v in d]
nx.draw(G,pos, linewidths=0, node_size = 5, with_labels = False, alpha = 0.5,font_size = 6, node_color='#C4272A', edge_color='#cccccc',arrows=True)
plt.savefig("graph_medias.png",dpi=200)

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

#transformer = StandardScaler()
#matrix = transformer.fit_transform(tfidf.todense())

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]

if "-tsne" in sys.argv :

  transformer = TfidfTransformer()
  tfidf = transformer.fit_transform(np.array(tweets))

  vectors = tfidf.todense()

  vecs = np.asfarray(vectors, dtype='float')

  Y = tsne.tsne(vecs, 2, 50, 20.0)

  k_means = KMeans(2, init='k-means++')

  k_means.fit(vecs)

  labels = k_means.labels_

  colors = []
  for key,lab in zip(keys,labels) :
    if key in inv :
      colors.append("#000000")
    else :
      colors.append("#CCCCCC")

  plt.scatter(Y[:,0], Y[:,1], s=10, color = colors)

  plt.savefig("tsne.png", dpi=200)

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
