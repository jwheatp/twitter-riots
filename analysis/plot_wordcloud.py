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

path = str(sys.argv[1])
out = str(sys.argv[2])

i = 0
words = {}
sets = {}
for filename in glob.glob(path):
  i = i + 1
  words[i] = []
  k = 0
  temp = []
  with open(filename) as f:
      for tweet in f:
        if math.fmod(k,100000) == 0 :
          print(k)
        tweet = re.findall('"((?:(?!(?:",")).)*)"',tweet)
        tokens = tweet[3].split(",")
        tokens = [x for x in tokens if x != "ferguson"]
        temp.extend(tokens)
        k = k + 1
  words[i] = Counter(temp).most_common(100)
  sets[i] = set([x[0] for x in words[i]])

print(words)
u = set.intersection(*sets.values())
print(u)
for l in words :
  # words[l] = [x for x in words[l] if x[0] not in u]
  woc = WordCloud(background_color="white", max_words=2000,width=1400,height=900,margin=0)
  woc.fit_words(words[l])
  plt.imshow(woc)
  plt.axis("off")
  plt.savefig('%s_%s' % (out,l),dpi=200)

def jaccardDist(a,b) :
  inter = a & b
  union = a | b
  return (float(len(inter))/float(len(union)))

jmatrix = numpy.zeros((10, 10))

for i in range(1,6) :
  for j in range(1,6) :
    dist = jaccardDist(sets[i],sets[j])
    jmatrix[i-1][j-1] = dist

print(jmatrix)

#text = ' '.join(words)

#wordcloud = WordCloud(background_color="white", max_words=2000,width=1400,height=900,margin=0).generate(text)

# Open a plot of the generated image.
#plt.imshow(wordcloud)
#plt.axis("off")
#plt.savefig(out,dpi=200)
