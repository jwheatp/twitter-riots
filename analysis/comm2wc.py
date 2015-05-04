"""Find hashtags communities from tweets

MIT License (MIT)

Copyright (c) 2015 Julien BLEGEAN <julien.blegean@aalto.fi>
"""
import os
import glob
import sys

# input tweets path
tweets = str(sys.argv[1])

print("")
print("1) Compute hashtag graph and find user communities")

# 
os.system("python hashtags.py %s" % tweets)
os.system("mv tcomm_* communities")
print("2) Group tweets")
os.system("python tweetsFromIds.py %s 'communities/tcomm_*'" % tweets)
os.system("mv ct_* communities")
print("3) Compute word clouds")
os.system("python plot_wordcloud.py 'communities/ct_*' communities/wc")
