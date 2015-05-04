import sys
import re
import datetime
from twarc import Twarc
import json
import csv
import os
import math
from collections import Counter
import random


def getOriginalTweets(tids) :

  def addTweet(tweet) :
    """ Process a tweet id and write the content in a csv file
    :params tweet : the tweet id
    """
    global i,outfile
    i = i + 1

    # show every 100 tweets processed
    if math.fmod(i,1000) == 0 :
      print(i)

    # FIELDS

    # retweet ?
    if tweet.has_key("retweeted_status") :
      # id
      t_id = '"%s"' % tweet["retweeted_status"]["id_str"].encode("ASCII",'ignore')

      # author
      author = '"%s"' % tweet["retweeted_status"]["user"]["id_str"].encode("ASCII",'ignore')

      # date
      created_at = tweet["retweeted_status"]["created_at"].encode("ASCII", 'ignore')
      created_at = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S')
      created_at = '"%s"' % created_at

      # content
      text = tweet["retweeted_status"]["text"].encode("ASCII", 'ignore')
      text = json.dumps(text)

      # tweet count
      rt_c = '"%s"' % str(tweet["retweet_count"])
      
      ido = tweet["id_str"]
      rt_lc = '"%s"' % str(tid2rtc[ido])
      # tweet query
      twt = [t_id,created_at,author,text,rt_c,rt_lc]
      top_rt.append(twt)

  # create Twarc instance to fetch from Twitter's API
  t = Twarc()

  top_rt = []

  # tweet counter
  i = 0

  tid2rtc = {}
  for tw in tids :
    tid2rtc[tw[0]] = tw[1]

  tids = [tid[0] for tid in tids]

  # iterate tweets
  for tweet in t.hydrate(tids):
    # process tweet id
    addTweet(tweet)
    
  top_rt = sorted(top_rt, key = lambda r : int(r[5][1:-1]),reverse = True)
  return top_rt




filepath = str(sys.argv[1])
outpath = str(sys.argv[2])

counter = Counter()

k = 0

time = []
keywords = []
keytags = []
totalt = 0
i = 0
for ar in sys.argv :
  i = i + 1
  if ar == "-h" :
    time.append(sys.argv[i])
    time.append(sys.argv[i+1])

id2tweet = {}

with open(filepath) as f:
    for tweet in f:
      if math.fmod(k,100000) == 0 :
        print(k)
      tweet = re.findall('"((?:(?!(?:",")).)*)"', tweet)

      k = k + 1

      tdate = datetime.datetime.strptime(tweet[1], '%Y-%m-%d %H:%M:%S')
      tdate = datetime.time(tdate.hour,tdate.minute)

      if len(time) > 0 :
        dfrom = datetime.datetime.strptime(time[0], '%H:%M')
        dfrom = datetime.time(dfrom.hour,dfrom.minute)

        dto = datetime.datetime.strptime(time[1], '%H:%M')
        dto = datetime.time(dto.hour,dto.minute)

      if len(time) == 0 or len(time) > 0 and tdate >= dfrom and tdate <= dto :
        totalt = totalt + 1
	txt = tweet[3]
        rt = re.findall(r"^RT @([a-zA-Z0-9-_]*): (.*)",txt)
        if len(rt) > 0 :
          rt = rt[0]        
          counter[(rt[0],rt[1])] += 1
          id2tweet[(rt[0],rt[1])] = tweet[0]

print("%s tweets found for the query" % totalt)

tuples = counter.most_common(10000)
print(tuples[:10])
tuples = [(id2tweet[u[0]],counter[u[0]]) for u in tuples]

top_rt = getOriginalTweets(tuples)

outp = open(outpath,'a')
for rt in top_rt :
  twt = '%s\n' % ','.join(rt)
  outp.write(twt)
