import sys
import math
import re
import nltk
from collections import Counter
import datetime
from nltk.probability import FreqDist
from nltk.classify import SklearnClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.pipeline import Pipeline
from sklearn import cross_validation
import numpy as np
from sklearn.metrics import f1_score

def genLabel(label_tuple) :
  return {
        (0,0): 0,
        (1,0): 1,
        (0,1): 2,
        (1,1): 3,
  }[label_tuple]


labelspath = str(sys.argv[1])

labels = open(labelspath).readlines()
labels = dict((l.strip().split(',')[0], genLabel(tuple(int(i) for i in l.strip().split(',')[1:3])) )for l in labels)

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

dataset = []

lab = []

training = []

filepath = str(sys.argv[2])

testing = []

print("# Training..")

with open("../../data/tweets/tweets_fw_11_08_p") as f:
    for tweet in f:
      if len(dataset) <= 500 :
        tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

        tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
        tdate = datetime.time(tdate.hour,tdate.minute)

        if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
          if "-medias" in sys.argv :
            tokens = re.findall('"((?:(?!(?:" ")).)*)"', tweet[12])
            tokens.extend(re.findall('"((?:(?!(?:",")).)*)"', tweet[13]))
            print(tokens)
          else :
            tokens = tweet[3].split(',')
          if "-shingling" in sys.argv :
            shingleLength = 3
            tokens = [" ".join(tokens[i:i+shingleLength]) for i in range(len(tokens) - shingleLength + 1)]
          if tweet[0] in labels :
            dataset.append(FreqDist(tokens))
            lab.append(labels[tweet[0]])

# model

def naivesBayes(classes_to_keep,classes_to_delete,labs,kf) :
  lab2 = lab

  classes = [l for l in [0,1,2,3] if l not in classes_to_delete]
  classes_to_merge = [l for l in classes if l not in classes_to_keep]
  lab2 = [l if l not in classes_to_merge else -1 for l in lab2]

  if len(classes_to_merge) > 0 :
    classes = classes_to_keep + [-1]

  pipeline = Pipeline([('nb', MultinomialNB())])
  classif = SklearnClassifier(pipeline)

  if len(classes_to_delete) > 0 :
    cvset = zip(dataset, lab2, labs)
    cvset = [tuple((l[0],l[1])) for l in cvset if l[2] == -1]
  else :
    cvset = zip(dataset,lab2)

  print("length dataset :")
  print(len(cvset))

  n_folds = kf

  cv = cross_validation.KFold(len(cvset), n_folds=n_folds, shuffle=False, random_state=None)

  accuracy = {}
  proport = {}
  proport_total = {}
  cardinal = {}

  for k in classes :
    accuracy[k] = []
    proport[k] = []
    cardinal[k] = len([l for l in cvset if l[1] == k])
    proport_total[k] = float(cardinal[k])/float(len(cvset))

  for traincv, testcv in cv:
    classifier = classif.train(cvset[traincv[0]:traincv[len(traincv)-1]])

    for k in classes :
      test = [l for l in cvset[testcv[0]:testcv[len(testcv)-1]] if l[1] == k]
      if len(test) > 0 :
        accuracy[k].append(nltk.classify.util.accuracy(classifier, test))
        proport[k].append(float(len(test))/cardinal[k])

  total_ac = []

  for k in classes :
    print("Class %s : " % k)
    #print(proport_total[k])
    mean = float(np.sum(np.multiply(proport[k],accuracy[k])))
    print(mean)
    total_ac.append(mean)

  print("total accuracy")
  print(np.sum(np.multiply(total_ac, proport_total.values())))

  new_labs = classif.classify_many(dataset)
  return new_labs, classif

def updatePredict(predict,labs) :
  for i in range(len(predict)) :
    if labs[i] != -1 :
      predict[i] = labs[i]
  return predict

# normal bayes
[ll,classif] = naivesBayes([0,1,2],[],lab,5)
print("-----------")

predict = [0]*500

# pairwise bayes
#labs = naivesBayes([0],[],lab,5)
#predict = updatePredict(predict,labs)
#print("-----------")
#labs = naivesBayes([1],[0],labs,4)
#predict = updatePredict(predict,labs)
#print("-----------")
#labs = naivesBayes([2],[1],labs,3)
#predict = updatePredict(predict,labs)
#print("###############")

#print(f1_score(labs,predict,average=None))

if "-tweetcl" in sys.argv :
  print("# Classification of tweets..")

  output = str(sys.argv[3])

  filepath = "../../data/tweets/tweets_fw_12_08_p"

  k = 0
  with open(filepath) as f:
      for tweet in f:
        if math.fmod(k,100000) == 0 :
          print(k)
        tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

        tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
        tdate = datetime.time(tdate.hour,tdate.minute)

        if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
          words = tweet[3].split(',')
          pclass = classif.classify(FreqDist(words))
          if pclass == -1 :
            pclass = 0
          out = '%s,%s\n' % (tweet[0],pclass)
          open(output,'a').write(out)

        k = k + 1

if "-usercl" in sys.argv :

  print("# Classification of users..")

  voting = {}

  k = 0
  with open(filepath) as f:
      for tweet in f:
        if math.fmod(k,100000) == 0 :
          print(k)
        tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

        tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
        tdate = datetime.time(tdate.hour,tdate.minute)

        if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
          words = tweet[3].split(',')
          pclass = classif.classify(FreqDist(words))
          if pclass == -1 :
            pclass = 0

          if tweet[2] not in voting :
            voting[tweet[2]] = Counter()
          voting[tweet[2]][pclass] += 1

        k = k + 1

  output = str(sys.argv[3])

  for user in voting :
    mc = voting[user].most_common()
    if len(mc) == 1 and int(mc[0][0]) == 0 :
      label = 0
    elif len(mc) > 1 and int(mc[0][0]) == 0 :
      label = int(mc[1][0])
    else :
      label = int(mc[0][0])
    out = '%s,%s\n' % (user,label)
    open(output,'a').write(out)
