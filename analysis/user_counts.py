"""get users counts

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""

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

# taken from

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

def process(user) :
  """ Process user id and add its content to csv file
  :param user: the user id
  """
  global i,usercounts
  i = i + 1

  if math.fmod(i,100) == 0 :
    print(i)

  # FIELDS

  # screen name
  u_screen_name = '"%s"' % user["screen_name"].encode("ASCII", 'ignore')
  u_screen_name = u_screen_name[1:-1].lower()

  # number of tweets
  u_tweets_count = '"%s"' % str(user["statuses_count"])
  u_tweets_count = int(u_tweets_count[1:-1])

  # number of followers
  u_followers_count = '"%s"' % str(user["followers_count"])
  u_followers_count = int(u_followers_count[1:-1])

  # number of friends
  u_friends_count = '"%s"' % str(user["friends_count"])
  u_friends_count = int(u_friends_count[1:-1])

  # group all the fields
  usercounts[u_screen_name] = tuple((u_tweets_count,u_followers_count,u_friends_count))

usercounts = {}
i = 0 

def getCounts(all_ids) :
  # counter

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
      # send by 100 chunks
      for k in range(0,len(all_ids),100) :
          idstr = ','.join(all_ids[k:k+100])
          r = requests.get("https://api.twitter.com/1.1/users/lookup.json?screen_name=%s" % idstr, auth=oauth)
          tlist = r.json()
          #print(tlist)
          while not isinstance(tlist, list) and tlist.has_key('errors') :
              print(tlist['errors'][0]['message'])
              print("Sleep for 60s..")
              time.sleep(60)
              r = requests.get("https://api.twitter.com/1.1/users/lookup.json?screen_name=%s" % idstr, auth=oauth)
              tlist = r.json()
          for user in tlist :
              process(user)

  return usercounts
