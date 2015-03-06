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
from sets import Set

path = str(sys.argv[1])
out = str(sys.argv[2])
i = 0
sets = {}
for filename in glob.glob(path):
  k = 0
  sets[i] = Set()
  with open(filename) as f:
      for user in f:
        if math.fmod(k,100000) == 0 :
          print(k)
        sets[i].add(user)
        k = k + 1        
  i = i + 1

def jaccardDist(a,b) :
  inter = a & b
  union = a | b
  return (float(len(inter))/float(len(union)))

jmatrix = numpy.zeros((len(sets), len(sets)))

for i in range(len(sets)) :
  for j in range(len(sets)) :
    dist = jaccardDist(sets[i],sets[j])
    jmatrix[i][j] = dist

print(jmatrix)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.set_aspect('equal')
plt.imshow(jmatrix, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar()
plt.savefig(out,dpi=200)
