"""Test doc 2 vec

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
from gensim import models
import tsne
from sklearn import metrics
from sklearn.cluster import KMeans,DBSCAN
from sklearn.preprocessing import scale

time = []
keytags = []
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


tlabels = open("../tclusters_info").readlines()
l = 0
labels = {}
for l in tlabels :
  kv = l.strip().split(",")
  uid = kv[0]
  labels[uid] = kv[1]

uulabels = open("uclusters_11_08_02_04").readlines()
l = 0
ulabels = {}
for l in uulabels :
  kv = l.strip().split(",")
  uid = kv[0]
  ulabels[uid] = kv[1]

topusers = open("../../../data/users/users_fw_11_08_10msg+").readlines()
topusers = set([u.strip().split(",")[1] for u in topusers])

filepath = str(sys.argv[1])

colors = []

tweets = {}

tweet2user = {}

total = 0

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
        if tweet[2] in topusers and labels[tweet[0]] == '1' and tweet[8] == '0':
          total = total + 1
          wds = tweet[3].split(",")
          wds = [unicode(w) for w in wds]
          if tweet[0] not in tweets :
            tweets[tweet[0]] = []
          tweets[tweet[0]] += wds
          tweet2user[tweet[0]] = tweet[2]
          #if labels[tweet[0]] == '0' :
          #  color = 'blue'
          #else :
          #  color = 'red'
          #  colors.append(color)
      k = k + 1

print(total)

pars = []

i = 0
for user in tweets :
  pars.append(models.doc2vec.LabeledSentence(words=tweets[user], labels=[u'USER_%s' % user]))
  i = i + 1


model = models.Doc2Vec(window=3, alpha=0.025, min_alpha=0.025)

model.build_vocab(pars)

for epoch in range(10):
    model.train(pars)
    model.alpha -= 0.002  # decrease the learning rate
    model.min_alpha = model.alpha  # fix the learning rate, no decay

#ms = model.most_similar('USER_34')
#for s in ms :
#  if "USER_" in s[0] :
#    print(pars[int(s[0][5:])])

def getColor(k) :
  """Homemade legend, returns a nice color for 0 < k < 10
  :param k : indice
  """
  colors = ["#862B59","#A10000","#0A6308","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536","#00ab7c"]
  return colors[k]

if "-tsne" in sys.argv :

  labels = []
  vectors = []
  users = []
  users_indexes = []

  for x in pars :
    key = x.labels[0]
    if key in model :
      vectors.append(model[key])
      labels.append(key)

  print(len(labels))

  vecs = np.asfarray(vectors, dtype='float')

  k_means = KMeans(10)

  Y = tsne.tsne(vecs, 2, 50, 20.0)

  #db = DBSCAN(eps=1.3).fit(Y)

  labels = k_means.labels_
  print(labels)

  k_means.fit(vecs)

  colors = [getColor(int(l)) for l in labels]

  i = 0
  tweets = {}
  for lab in labels :
    if lab not in tweets :
      tweets[lab] = []
    tweets[lab].append(pars[i])
    i = i + 1

  for key in tweets :
    print("cluster %s" % key)
    for t in tweets[key] :
      print(t)

#  centroids = k_means.cluster_centers_

#  plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=100, linewidths=2, color='b', zorder=10)
  plt.scatter(Y[:,0], Y[:,1], s=30, color = colors)

  plt.savefig("tsne.png", dpi=200)
