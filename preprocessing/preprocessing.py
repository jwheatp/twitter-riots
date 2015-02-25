# imports
import json
import math
import sys
import nltk
import re
import csv
from datetime import datetime,timedelta

# global variables
lancaster = nltk.LancasterStemmer()

def tokenize(raw) :
    """Tokenizing a string"""
    return nltk.word_tokenize(raw)

def stem(tokens) :
    """Stemming tokens"""
    return [lancaster.stem(t) for t in tokens]

# not used at the moment, too long
def lem(tokens) :
    """Lemmitizating tokens"""
    return [wnl.lemmatize(t) for t in tokens]

def rmStops(tokens) :
    """Remove stop words"""
    filtered_words = [w for w in tokens if not w in nltk.corpus.stopwords.words('english')]
    return filtered_words

def rmHtml(string):
    return re.findall('>(.*)<', string)

def rmPunct(string) :
    """Remove punctuation"""
    return re.sub(r'[^\w\s]','',string)

def rmAts(string) :
    """Remove '@' mentions"""
    return re.sub(r'@\w+', '', string)

def rmHTs(string) :
    """Remove hashtags"""
    return re.sub(r'#\w+', '', string)

def rmRTs(tokens) :
    """Remove RTs"""
    return [x for x in tokens if x != "rt"]

def rmLinks(string) :
    """Remove links"""
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', string)

def clean(raw) :
    """Clean a tweet - All the preprocess in one function"""
    raw = raw.lower()
    raw = rmLinks(raw)
    raw = rmAts(raw)
    raw = rmHTs(raw)
    raw = rmPunct(raw)
    tokens = tokenize(raw)
    tokens = rmStops(tokens)
    if len(tokens) > 0 and tokens[0] == "rt" :
      isRT = True
    else :
      isRT = False
    tokens = rmRTs(tokens)
    return tokens,isRT

def processTweet(tweet) :
  global i,outfile
  i = i + 1

  if math.fmod(i,100) == 0 :
    print(i)

  tweet = re.findall(r'"((?:(?!(?:",")).)*)"',tweet)  

  tweet[13] = rmHtml(tweet[13])
  if len(tweet[13]) > 0 :
    tweet[13] = tweet[13][0]
  else :
    tweet[13] = 'null'

  mentions = re.findall(r'@\w+', tweet[3])
  mentions = [s[1:] for s in mentions]
  mentions = ','.join(mentions)

  tweet[3],isRT = clean(tweet[3])
  tweet[3] = ','.join(tweet[3])

  tweet.insert(10,mentions)

  if isRT :
    isRT = '1'
  else :
    isRT = '0'
  tweet.insert(8,isRT)

  tweet = ['"%s"' %s for s in tweet]

  tweet = ','.join(tweet)

  with open(outpath, "a") as file:
    file.write('%s\n' % tweet)

# counter
i = 0

filepath = str(sys.argv[1])

outpath = "%s_p" % filepath

# iterate tweets
with open(filepath) as f:
    for tweet in f:
        processTweet(tweet)
