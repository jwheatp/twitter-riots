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

def checkUsers(u_id,f_ids) :
  global outfile

  ids = all_ids.intersection(f_ids)
  ids = list(ids)
  ids.insert(0,u_id)
  ids = '%s\n' % ','.join(ids)

  with open(outpath, "a") as file:
    file.write(ids)

# counter
i = 0

filepath = str(sys.argv[1])

outpath = "%s_fh" % filepath

allIdsFile = str(sys.argv[2])

file = open(allIdsFile)
all_ids = file.readlines()
all_ids = [id.strip() for id in all_ids]
all_ids = set(all_ids)

def fetchFollowers(user_id) :
  r = requests.get("https://api.twitter.com/1.1/friends/ids.json?user_id=%s" % user_id, auth=oauth)
  return r.json()

if not OAUTH_TOKEN:
    token, secret = setup_oauth()
    print "OAUTH_TOKEN: " + token
    print "OAUTH_TOKEN_SECRET: " + secret
    print
else:
    oauth = get_oauth()
    # iterate tweets

    k = 0
    with open(filepath) as f:
      for user in f:
        if math.fmod(k,10) == 0 :
          print(k)
        k = k + 1
        user_id = str(user.strip())

        ulist = fetchFollowers(user_id)

        while not isinstance(ulist, list) and ulist.has_key('errors') :
            print(ulist['errors'][0]['message'])
            print("Sleep for 60s..")
            time.sleep(60)
            ulist = fetchFollowers(user_id)

        checkUsers(user_id,ulist["ids"])

