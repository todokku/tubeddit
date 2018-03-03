from random import randint
botPhrase = ["A dog has an owner. A cat has a staff. Since I have an owner, I am a dog, not a bot!","Being an adult is just walking around wondering what you're forgetting.","If you call me a bad bot, I will cry real tears!","Am I a good bot?","I hate people who use big words just to make themselves look perspicacious.","I named my dog 6 miles so I can tell people that I walk 6 miles every single day.","When I found out that my toaster wasn't waterproof, I was shocked.","I saw my dad chopping up onions today and I cried. Onions was a good dog."]
myComment = "--------------------\n"
myComment += "   [Youtube Mirror](" + botPhrase[randint(0, 5)] + ")   \n"
myComment += "--------------------"
print myComment

print randint(0, len(botPhrase) - 1)


print "A dog has an owner. A cat has a staff. Since I have an owner, I am a dog, not a bot!".replace(' ', ' ^')


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


from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


argsdict = {}
d=1
fileN = ''
description = ''
title = ''
privacyStatus = 'public'
category = '20'
keywords="overwatch gameplay,overwatch live,overwatch 2017,overwatch funny,overwatch,overwatch game,overwatch new,overwatch latest,overwatch, gameplay,overwatch funny moments,moira gameplay, moira, overwatch moira, moira overwatch, blizzard, overwatch ps4, overwatch moments, overwatch blizzcon, overwatch new hero"
botPhrase = ["A dog has an owner. A cat has a staff. Since I have an owner, I am a dog, not a bot!","Being an adult is just walking around wondering what you're forgetting.","If you call me a bad bot, I will cry real tears!","Am I a good bot?","I hate people who use big words just to make themselves look perspicacious.","I named my dog 6 miles so I can tell people that I walk 6 miles every single day.","When I found out that my toaster wasn't waterproof, I was shocked.","I saw my dad chopping up onions today and I cried. Onions was a good dog."]
# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("upload_video.py-oauth2.json")
  credentials = storage.get()



  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  tags = options['keywords'].split(",")

  body=dict(
    snippet=dict(
      title=options['title'],
      description=options['description'],
      tags=tags,
      categoryId=options['category']
    ),
    status=dict(
      privacyStatus=options['privacyStatus']
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if 'id' in response:
        myComment = "[Youtube Mirror](" + "https://www.youtube.com/watch?v=" + response['id'] + ")   \n***\n"
        myComment += "^" + botPhrase[randint(0, len(botPhrase) - 1)].replace(' ', ' ^')
        os.environ['http_proxy'] = "http://34.214.213.90:8888"
        os.environ['https_proxy'] = "http://34.214.213.90:8888"
        submission.reply(myComment)
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        print "Video id '%s' was successfully uploaded." % response['id']
        print 'Sleeping'
        sleep(600)
      else:
        exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)

if __name__ == '__main__':
  basedir = 'downloads/'

  reddit = praw.Reddit(
           )
  c = 0
  for submission in reddit.subreddit('Overwatch').stream.submissions():
    c += 1
    if c<=75:
      print c
      continue
    
    try:
      print c
      if(submission.url.find("clips.twitch.tv") != -1):
        d+=1
        url = submission.url.replace('?tt_medium=redt', '')
        channel = url.split('/')[2]
        filename = url.split('/')[3]
        outputpath = (basedir + '/' + filename + '.mp4').replace('\n', '')
        print outputpath
        if not os.path.exists(basedir + '/'):
          os.makedirs(basedir + '/')
        html = str(urllib2.urlopen(url).read())
        mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
        urllib.urlretrieve(mp4url, outputpath)
        channel = url.split('/')[2]
        filename = url.split('/')[3]
        outputpath = (basedir + '/' + filename + '.mp4').replace('\n', '')
        fileN = outputpath
        if not os.path.exists(basedir + '/'):
          os.makedirs(basedir + '/')
        title = submission.title
        description = 'Join the discussion on Reddit.\n\nReddit: https://www.reddit.com/r/Overwatch/comments/' + submission.id + '\nTwitch Stream: ' + url + '\n\nLike, share and subscribe to our channel for daily Overwatch live gameplay videos!\nHelp us reach 100 subscribers\n\nAll the music and video copyrights are owned by their respective copyright holders.'
        html = str(urllib2.urlopen(url).read())
        mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
        urllib.urlretrieve(mp4url, outputpath)


        argsdict['file'] = fileN
        argsdict['title'] = title + ' | Overwatch Gameplay'
        argsdict['description'] = description
        argsdict['category'] = category
        argsdict['keywords'] = keywords
        argsdict['privacyStatus'] = privacyStatus
        youtube = get_authenticated_service(argsdict)
        print argsdict
        try:
          initialize_upload(youtube, argsdict)
          print 'Sleeping'
          sleep(20)
        except HttpError, e:
          print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
    except Exception, e:
      print e
      continue;


