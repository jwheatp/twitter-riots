# imports
from twarc import Twarc
from datetime import datetime
import json
import math
import sys
import csv

def addTweet(tweet) :
  global i,outfile
  i = i + 1

  if math.fmod(i,100) == 0 :
    print(i)

  # tweets fields

  # id
  t_id = '"%s"' % tweet["id_str"].encode("ASCII",'ignore')

  # author
  author = '"%s"' % tweet["user"]["id_str"].encode("ASCII",'ignore')

  # date
  created_at = tweet["created_at"].encode("ASCII", 'ignore')
  created_at = datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S')
  created_at = '"%s"' % created_at

  # content
  text = tweet["text"].encode("ASCII", 'ignore')
  text = json.dumps(text)

  # in reply tweet id
  in_reply_to = tweet["in_reply_to_status_id_str"]

  # in reply user id
  in_reply_to_u = tweet["in_reply_to_user_id_str"]

  if in_reply_to == None :
    in_reply_to = '"null"'
    in_reply_to_u = '"null"'
    is_reply = '"0"'
  else :
    is_reply = '"1"'
    in_reply_to = '"%s"' % in_reply_to.encode("ASCII","ignore")
    in_reply_to_u = '"%s"' % in_reply_to_u.encode("ASCII","ignore")

  # retweet count
  retweet_count = '"%s"' % tweet["retweet_count"]

  # favourite count
  favorite_count = '"%s"' % tweet["favorite_count"]

  # lang
  lang = tweet["lang"].encode("ASCII", 'ignore')
  lang = '"%s"' % lang

  #hashtags list
  ht_list = []
  entities = tweet["entities"]
  if entities.has_key("hashtags") :
    for hashtag in tweet["entities"]["hashtags"] :
      tag = hashtag["text"].encode("ASCII","ignore")
      ht_list.append(tag)

  ht = ' '.join(ht_list)
  ht = '"%s"' % ht
  # urls
  url_list = []
  if entities.has_key("urls") :
    for url in tweet["entities"]["urls"] :
      urlc = json.dumps(url["expanded_url"].encode("ASCII","ignore"))
      url_list.append(urlc)

  url_l = ' '.join(url_list)
  url_l = '"%s"' % url_l
  # medias
  media_list = []
  if entities.has_key("media") :
    for media in tweet["entities"]["media"] :
      media_list.append(json.dumps(media["media_url"].encode("ASCII","ignore")))

  medias_l = ' '.join(media_list)
  medias_l = '"%s"' % medias_l
  # source
  source = tweet["source"].encode("ASCII", "ignore")
  source = json.dumps(source)

  # retweet ?
  if tweet.has_key("retweeted_status") :
    retweeted = '"1"'
    retweeted_id = tweet["retweeted_status"]["id_str"].encode("ASCII","ignore")
  else :
    retweeted = '"0"'
    retweeted_id = '"null"'

  # coordinates ?
  if tweet["coordinates"] ==  None :
    lat = '"null"'
    lon = '"null"'
    geo = '"0"'
  else :
    lon = '"%s"' % tweet["coordinates"]["coordinates"][0]
    lat = '"%s"' % tweet["coordinates"]["coordinates"][1]
    geo = '"1"'

  # tweet query
  twt = [t_id,created_at,author,text,is_reply,in_reply_to,in_reply_to_u,retweet_count,favorite_count,ht,url_l,medias_l,lang,source,geo,lon,lat]
  twts = '%s\n' % ','.join(twt)

  with open(outpath, "a") as file:
    file.write(twts)

t = Twarc()

# counter
i = 0

filepath = str(sys.argv[1])

outpath = "%s_h" % filepath

# iterate tweets
for tweet in t.hydrate(open(filepath)):
  addTweet(tweet)
