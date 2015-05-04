"""Content cluster

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
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram,fcluster
from operator import itemgetter
import sys
from collections import Counter
import random
from pylab import rcParams
import pylab as pl

def tronc(f) :
  return float("{0:.4f}".format(f))

def tfidf(topwords,counter,docNumb) :
  docLen = len(topwords)
  tfidf_values = {}
  for word in topwords :
    tf = float(float(word[1])/float(docLen))
    idf = float(float(docNumb)/float(counter[word[0]]))
    idf = math.log(idf)
    tfidf_values[word[0]] = tronc(float(float(tf)*float(idf)))
  return tfidf_values

def cosine(x,y) :
  inter = set(x.keys()) & set(y.keys())
  prod = 0
  for c in inter :
    prod += tronc(x[c]*y[c])
  denom = tronc(float(np.linalg.norm(x.values()))*float(np.linalg.norm(y.values())))
  if denom == 0 :
    return 1.57
  d = float(float(prod)/float(denom))
  return d


def clusterize(user2tweets, allTweetsCounter, allHtagsCounter, allMentionsCounter) :
  o = 0
  docNumb = len(user2tweets)
  user2tweets = sorted(user2tweets.items(), key=lambda x : int(x[1][0]), reverse = True)[:100]
  for user in user2tweets :
    user2tweets[o] = list(user2tweets[o])
    topwords = user2tweets[o][1][1].most_common(100)
    tophts = user2tweets[o][1][2].most_common(100)
    topmentions = user2tweets[o][1][3].most_common(100)

    user2tweets[o][1][1] = tfidf(topwords,allTweetsCounter,docNumb)
    user2tweets[o][1][2] = tfidf(tophts,allHtagsCounter,docNumb)
    user2tweets[o][1][3] = tfidf(topmentions,allMentionsCounter,docNumb)
    o = o + 1

  nusers = len(user2tweets)

  dist_matrix = np.zeros((nusers,nusers))

  user2tweets = list(user2tweets)

  for i in range(nusers) :
    for j in range(nusers) :
      dist_matrix[i][j] = cosine(user2tweets[i][1][1],user2tweets[j][1][1])
      dist_matrix[i][j] += cosine(user2tweets[i][1][2],user2tweets[j][1][2]) 
      dist_matrix[i][j] += cosine(user2tweets[i][1][3],user2tweets[j][1][3])
      dist_matrix[i][j] /= 3 

  dist_matrix = dist_matrix.clip(0)

  pl.pcolor(dist_matrix)
  pl.colorbar()
  plt.savefig("heatmap.png",dpi=200)

  nc = 1.4

  clusters = linkage(dist_matrix)
  flat_clusters = fcluster(clusters,nc,"distance")

  cluster2users = {}
  cluster2htags = {}
  for i in range(nusers) :
    if flat_clusters[i] not in cluster2users : 
      cluster2users[flat_clusters[i]] = []
      cluster2htags[flat_clusters[i]] = set()
    user2tweets[i][1][1] = sorted(user2tweets[i][1][1].items(), key = lambda x : float(x[1]),reverse=True)[:10]
    user2tweets[i][1][2] = sorted(user2tweets[i][1][2].items(), key = lambda x : float(x[1]),reverse=True)[:10]
    user2tweets[i][1][3] = sorted(user2tweets[i][1][3].items(), key = lambda x : float(x[1]),reverse=True)[:10]
    
    cluster2users[flat_clusters[i]].append(user2tweets[i])

    htset = set(cluster2htags[flat_clusters[i]]) | set(tag[0] for tag in user2tweets[i][1][2] if tag[0] not in ["ferguson","mikebrown"])
    cluster2htags[flat_clusters[i]] = htset

  r = redis.StrictRedis(host='localhost', port=6379, db=0)

  clusters2names = {}

  for c in cluster2users :
    clusters2names[c] = []
    for u in cluster2users[c] :
      name = r.get(u[0])
      if not name == None :
        clusters2names[c].append(r.get(u[0]).split(",")[1][1:-1].lower())

  print(cluster2htags)
  return clusters2names

if "-process" in sys.argv :
  filepath = str(sys.argv[1])

  user2tweets = {}

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

  allTweetsCounter = Counter()
  allHtagsCounter = Counter()
  allMentionsCounter = Counter()

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
        k = k + 1
  clusterize(user2tweets, allTweetsCounter, allHtagsCounter, allMentionsCounter)