import httplib
import httplib2
import os
import random
import sys
import time

import urllib2
import urllib

import praw
from time import sleep
from random import randint
import re
reddit = praw.Reddit(
           )
for submission in reddit.subreddit('leagueoflegends').stream.submissions():
  print(submission.author)
