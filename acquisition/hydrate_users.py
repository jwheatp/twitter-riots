# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
import json
import math
import sys
import csv
import os
import time
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

OAUTH_TOKEN = os.environ.get('ACCESS_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

def addUser(user) :
  global i,outfile
  i = i + 1

  if math.fmod(i,100) == 0 :
    print(i)

  # user fields
  u_id = '"%s"' % user["id_str"].encode("ASCII","ignore")

  u_name = user["name"].encode("ASCII", 'ignore')
  u_name = json.dumps(u_name)

  u_screen_name = '"%s"' % user["screen_name"].encode("ASCII", 'ignore')

  u_created_at = user["created_at"].encode("ASCII", 'ignore')
  u_created_at = '"%s"' % datetime.strptime(u_created_at, '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S')

  u_location = user["location"].encode("ASCII", 'ignore')
  u_location = json.dumps(u_location)

  u_tweets_count = '"%s"' % str(user["statuses_count"])

  u_followers_count = '"%s"' % str(user["followers_count"])

  u_friends_count = '"%s"' % str(user["friends_count"])

  u_favourites_count = '"%s"' % str(user["favourites_count"])

  u_listed_count = '"%s"' % str(user["listed_count"])

  if user["time_zone"] == None :
    u_time_zone = 'NULL'
  else :
    u_time_zone = user["time_zone"].encode("ASCII","ignore")
    u_time_zone = json.dumps(u_time_zone)

  # tweet query
  usr = [u_id,u_name,u_screen_name,u_created_at,u_location,u_tweets_count,u_followers_count,u_friends_count,u_favourites_count,u_listed_count,u_time_zone]
  usrs = '%s\n' % ','.join(usr)

  with open(outpath, "a") as file:
    file.write(usrs)

# counter
i = 0

filepath = str(sys.argv[1])

file = open(filepath)
all_ids = file.readlines()
all_ids = [id.strip() for id in all_ids]

outpath = "%s_h" % filepath

if not OAUTH_TOKEN:
    token, secret = setup_oauth()
    print "OAUTH_TOKEN: " + token
    print "OAUTH_TOKEN_SECRET: " + secret
    print
else:
    oauth = get_oauth()
    # iterate tweets
    k = 0
    ids = []
    for k in range(0,len(all_ids),100) :
        idstr = ','.join(all_ids[k:k+100])
        r = requests.get("https://api.twitter.com/1.1/users/lookup.json?user_id=%s" % idstr, auth=oauth)
        tlist = r.json()
        #print(tlist)
        while not isinstance(tlist, list) and tlist.has_key('errors') :
            print(tlist['errors'][0]['message'])
            print("Sleep for 60s..")
            time.sleep(60)
            r = requests.get("https://api.twitter.com/1.1/users/lookup.json?user_id=%s" % idstr, auth=oauth)
            tlist = r.json()
        for user in tlist :
            addUser(user)
