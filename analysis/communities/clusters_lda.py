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
import lda
from gensim import models
from gensim import corpora, models, matutils
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import feature_extraction
from sklearn.cluster import DBSCAN
import re 

def clusterize(tweets) :
  #transformer = TfidfTransformer()
  #tfidf = transformer.fit_transform(np.array(tweets.values()))

  if "-lda" in sys.argv : 
    tfidf = models.tfidfmodel.TfidfModel(tweets.values())
    corpus = tfidf[tweets.values()]
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word = dicog,num_topics=5)
    topics = lda.print_topics(5, 10)
    for topic in topics : 
      topic = re.sub(r'([0-9\.]*)\*','', topic)
      print(topic)

  if "-lsi" in sys.argv :
    tfidf = models.tfidfmodel.TfidfModel(tweets.values())
    corpus = tfidf[tweets.values()]
    lsi = models.lsimodel.LsiModel(corpus=corpus, id2word = dicog,num_topics=5)
    topics = lsi.print_topics(5, 10)
    for topic in topics :
      topic = re.sub(r'([0-9\.]*)\*','', topic)
      print(topic)

 
#    model = lda.LDA(n_topics=5, n_iter=500, random_state=1)
#    model.fit(tfidf.toarray())
#    topic_word = model.topic_word_  # model.components_ also works
#    n_top_words = 10

#    for i, topic_dist in enumerate(topic_word):
#      topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
#      print('Topic {}: {}'.format(i, ' '.join(topic_words)))

  if "-dbscan" in sys.argv :
    db = DBSCAN(eps=1.1).fit(tfidf.toarray())

    labels = db.labels_
    print(len(labels))

    clusters = {}
    for i in range(len(labels)) : 
      if labels[i] not in clusters :
        clusters[labels[i]] = []
      clusters[labels[i]].append(tweets.keys()[i])
 
    for c in clusters : 
      print(" ")
      print("cluster %s " % c)
      print("------------")
      i  = 0
      for tid in clusters[c] :
        i += 1
        if i == 30 :
          break
        print(vec2bow(tweets[tid]))

  return 0

def bow2vec(words) :
  words = dict(words)
  return [words[x] if x in words else 0 for x in vocab]

def vec2bow(vec) :
  words = []
  for v in range(len(vec)) :
    if vec[v] != 0 :
      words.append(vocab[v])
  return words

if "-process" in sys.argv :
  filepath = str(sys.argv[1])

  # redis connection
  rt = redis.StrictRedis(host='localhost', port=6379, db=1)
  r = redis.StrictRedis(host='localhost', port=6379, db=0)

  plabels = open("../sc_11_02_04").readlines()
#  plabels = open("../tclusters_info").readlines()
  l = 0
  labels = {}
  for l in plabels :
    kv = l.strip().split(",")
    uid = kv[0]
    labels[uid] = kv[1]

  vocab = open("dictionary_11_08").readlines()
  vocab = [v.strip() for v in vocab]

  tweets = {}

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

  if "-lda" in sys.argv or "-lsi" in sys.argv : 
    dicog = corpora.Dictionary.load("dictionary_gensim_11_08")

  vectorizer = feature_extraction.text.CountVectorizer()

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
          tid = tweet[0]
          words = tweet[3].split(",")
          words = [w for w in words if w not in ["amp","ferguson",""] and not w.isdigit()]
          if len(words) > 3 and int(labels[tweet[0]]) == 2:
            counts = Counter(words).most_common()
            vec = bow2vec(counts)
            if sum(vec) > 0 :
              if "-lda" in sys.argv or "-lsi" in sys.argv :
                tweets[tid] = dicog.doc2bow(words)
              else :
                tweets[tid] = vec
        k = k + 1
  print("%s tweets founds." % len(tweets))
  clusterize(tweets)
