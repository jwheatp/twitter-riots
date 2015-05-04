from os import path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import sys
import re
import glob
import numpy

def correlations(communities) :
        n = len(communities)
	i = 0
	sets = {}
	for com in communities :
		com = communities[com]
		i = i + 1
		k = 0
		sets[i] = set()

		for tweet in com :
			if math.fmod(k,100000) == 0 :
				print(k)
			sets[i].add(tweet[0])

			k = k + 1

	def jaccardDist(a,b) :
	  inter = a & b
	  union = a | b
	  return (float(len(inter))/float(len(union)))

	jmatrix = numpy.zeros((n, n))

	for i in range(1,n) :
	  for j in range(1,n) :
	    dist = jaccardDist(sets[i],sets[j])
	    jmatrix[i-1][j-1] = dist

	print(jmatrix)
