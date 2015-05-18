import sys
import math
import re
import nltk
from collections import Counter
import datetime
from nltk.probability import FreqDist
from nltk.classify import SklearnClassifier
from sklearn.feature_extraction.text import TfidfTransformer,TfidfVectorizer,CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.pipeline import Pipeline
from sklearn import cross_validation
from sklearn.svm import LinearSVC
import numpy as np
from sklearn.metrics import f1_score,accuracy_score,precision_recall_fscore_support,classification_report
import argparse

##########################################
## Arguments
##########################################

parser = argparse.ArgumentParser(description='Generate hashtags graphs')

parser.add_argument('--filepath', dest='filepath',
                   help='path of the tweets file')

parser.add_argument('--labelspath', dest='labelspath',
                   help='path of the labels file')

parser.add_argument('--output', dest='output', default="graph_hashtags.png",
                   help='graph output name')

parser.add_argument('--time', dest='time', nargs=2,
                   help='time window')

parser.add_argument('--medias', dest='medias', action="store_true",
                   help='medias ?')

parser.add_argument('--mediaspath', dest='mediaslabelspath',
                   help='path of the medias labels file')

parser.add_argument('--shingling', dest='shingling', action="store_true",
                   help='shingling ?')

parser.add_argument('--shingLength', dest='shinglingLength', type=int,
                   help='shingling?')

parser.add_argument('--tweetcl', dest='tweetcl', type=bool, default=False,
                   help='tweet cl?')

parser.add_argument('--tweetcl_filepath', dest='tweetcl_filepath',
                   help='path of the tweets file')

parser.add_argument('--tweetcl_output', dest='tweetcl_output', default="tweetcl",
                   help='graph output name')

parser.add_argument('--usercl', dest='usercl', type=bool, default=False,
                   help='usercl?')

parser.add_argument('--usercl_filepath', dest='usercl_filepath',
                   help='path of the tweets file')

parser.add_argument('--usercl_output', dest='usercl_output', default="usercl",
                   help='graph output name')

parser.set_defaults(medias=False)

parser.set_defaults(shingling=False)

args = parser.parse_args()

##########################################
## Functions
##########################################

def genLabel(label_tuple) :
  return {
        # garbage class
        (0,0): 0,
        # informative class
        (1,0): 1,
        # biased class
        (0,1): 2,
        # informative and biased class
        (1,1): 3,
  }[label_tuple]

##########################################
## Data acquisition
##########################################

# get the 500 manual labels from the 11/08 riot night
# the labels are pairs labels (informative,biased)
labels = open(args.labelspath).readlines()

# build a <tweet_id, label> dictionary
# the labels are 0,1,2,3 from the genLabel function
labels = dict((l.strip().split(',')[0], genLabel(tuple(int(i) for i in l.strip().split(',')[1:3])) )for l in labels)

if args.medias : 

  # get the 100 medias labels from the 11/08 riot night
  medias_labels = open(args.mediaslabelspath).readlines()

  # build a <media_url, label> dictionary
  # the labels are 1,2
  medias_labels = dict(tuple((l.strip().split(',')[0],int(l.strip().split(',')[1]))) for l in medias_labels)

  test_ml = dict(medias_labels.items()[-20:])
  medias_labels = dict(medias_labels.items()[:80])

# time window 
time = []
if args.time != None :
  time = args.time

if len(time) > 0 :
  dfrom = datetime.datetime.strptime(time[0], '%H:%M')
  dfrom = datetime.time(dfrom.hour,dfrom.minute)

  dto = datetime.datetime.strptime(time[1], '%H:%M')
  dto = datetime.time(dto.hour,dto.minute)

# all the 500 labeled tweets
dataset = []

# labels
lab = []

# input tweets file
filepath = str(args.filepath)

# shingling sizes
shingleLength = args.shinglingLength

print("# Acquisition..")

with open(args.filepath) as f:

    # for each tweet
    for tweet in f:

      # if we have all our tweets, we can stop
      #if len(dataset) >= 500 :
      #  break

      # parsing tweet
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      if tweet[8] == '1' :
        continue

      if tweet[3] == '' :
        continue

      # time process
      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      # if it is in our time window
      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :

        # medias process
        if args.medias :
          medias = re.findall('"((?:(?!(?:" ")).)*)"', tweet[12])
          medias.extend(re.findall('"((?:(?!(?:",")).)*)"', tweet[13]))
          medintersec = set(medias_labels.keys()).intersection(medias)
          medintersec2 = set(test_ml.keys()).intersection(medias)

        # shingling processing ?
        if args.shingling :
          # get the text content
          tokens = tweet[3].split(',')
          # generate shinglings
          tokens = [" ".join(tokens[i:i+shingleLength]) for i in range(len(tokens) - shingleLength + 1)]

        if args.medias and medintersec and tweet[3] not in dataset :
          medintersec = list(medintersec)[0]
          # add bag of words to dataset
          dataset.append(tweet[3])
          tlab = medias_labels[medintersec]
          lab.append(tlab)
        elif tweet[0] in labels and not args.medias :
          # add bag of words to dataset
          dataset.append(tweet[3])
          tlab = labels[tweet[0]]
          lab.append(tlab)

##########################################
## Cross-validation training / testing
##########################################

# class pairNaiveBayes :

#   def __init__(self) :
#     self.classifier1 = SklearnClassifier(MultinomialNB())
#     self.classifier2 = SklearnClassifier(MultinomialNB())

#   def train(self,rows) :
#     [rows,rlabels] = zip(*rows)
#     # 1 - our classes are 0 and (1,2), so we group classes 1 and 2 to a class called -1
#     rlabels1 = [-1 if l in (1,2) else l for l in rlabels]
#     classes = (-1,0)

#     # 2 - our <dataset,labels>
#     dset = zip(rows,rlabels1)

#     # 3 - train first classifier
#     self.classifier1 = self.classifier1.train(dset)

#     # 4 - our classes are now 1 and 2
#     dset = zip(rows,rlabels)
#     dset = [r for r in dset if r[1] != 0]

#     # 5 - train second classifier
#     self.classifier2 = self.classifier2.train(dset)

#   def predict(self,rows) :
#     # 1- first classifier returns 0 and -1 labels
#     lab1 = self.classifier1.classify_many(rows)

#     # 2 - select rows for second classifier
#     rows = [r for r,l in zip(rows,lab1) if l == -1]

#     # 3 - second classifier returns 1 and 2 labels
#     lab2 = self.classifier2.classify_many(rows)

#     # 4 - returns predicted labels
#     rlabels = []
#     k = 0
#     for l in lab1 :
#       if l == 0 :
#         rlabels.append(0)
#       else :
#         rlabels.append(lab2[k])
#         k += 1

#     return rlabels

##################################

# model
n_folds = 10

# initialize Multinomial Naive Bayes Classifier
tr = CountVectorizer()
mnb = MultinomialNB()
classifier = Pipeline([('counts', tr),
                     ('nb', mnb)])

# zip tweets and labels for training/testing
cvset = zip(dataset,lab)
# remove class 3 rows
cvset = [l for l in cvset if l[1] != 3]

# cross validation indexes
cv = cross_validation.KFold(len(cvset), n_folds=n_folds, shuffle=True, random_state=None)

accs_d = []
accs = []

accs_d_p = []
accs_p = []

# for each train/test set :
for traincv, testcv in cv :
  # given the indexes, take the rows
  # 1) training set
  traincv = [cvset[l] for l in traincv]
  [traincv_data, traincv_labels] = zip(*traincv)

  # 2) testing set (tweets)
  testcv_data = [cvset[l][0] for l in testcv]

  # 3 ) testing set (labels)
  testcv_labels = [cvset[l][1] for l in testcv]

  # train the classifier
  classifier.fit(traincv_data,traincv_labels)
  # and predict test labels
  test_preds = classifier.predict(testcv_data)

  # compute F1 score for each class
  accuracy = f1_score(testcv_labels,test_preds,average=None, labels=[0,1,2])
  accs_d.append(accuracy)

  # and average weighted
  acc_average = f1_score(testcv_labels,test_preds,average="weighted", labels=[0,1,2])
  accs.append(acc_average)

  ################################
  ################################

  # # train the classifier
  # classifier_p = pairNaiveBayes()
  # classifier_p.train(traincv)
  # # and predict test labels
  # test_preds = classifier_p.predict(testcv_data)

  # # compute F1 score for each class
  # accuracy = f1_score(testcv_labels,test_preds,average="samples", labels=[0,1,2])
  # accs_d_p.append(accuracy)

  # # and average weighted
  # acc_average = f1_score(testcv_labels,test_preds,average="weighted", labels=[0,1,2])
  # accs_p.append(acc_average)

accs_d = np.array(accs_d)
accs_d = np.mean(accs_d,axis=0)
print(accs_d)

accs = np.mean(accs)
print(accs)

classifier.fit(dataset,lab)

def print_top10(vectorizer, clf, class_labels):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names()
    for i, class_label in enumerate(class_labels):
        top10 = np.argsort(clf.coef_[i])[-15:]
        print("%s: %s" % (class_label,
              " ".join(feature_names[j] for j in top10)))

print_top10(tr,mnb,[0,1,2])

# print("-------------")

# accs_d_p = np.array(accs_d_p)
# accs_d_p = np.mean(accs_d_p,axis=0)
# print(accs_d_p)

# accs_p = np.mean(accs_p)
# print(accs_p)

##########################################
## Tweet classification
##########################################

if args.tweetcl :
  print("# Classification of tweets..")

  output = args.tweetcl_output

  k = 0
  with open(args.tweetcl_filepath) as f:
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

##########################################
## User classification
##########################################

if args.usercl :

  print("# Classification of users..")

  voting = {}

  k = 0
  with open(args.usercl_filepath) as f:
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

  output = args.usercl_output

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
