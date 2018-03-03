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

fileN = ''
description = ''
title = ''
privacyStatus = 'public'
category = '20'
keywords="league of legends gameplay,league of legends live,league of legends 2017,league of legends funny,league of legends,league of legends game,league of legends new,league of legends latest"

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

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
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

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
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
        print "Video id '%s' was successfully uploaded." % response['id']
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

  for submission in reddit.subreddit('leagueoflegends').new(limit = None):
    if(submission.selftext.find("clips.twitch.tv") != -1):
      url = re.search("(?P<url>https?://clips[^\s]+)", submission.selftext).group("url").replace(')', '')
      channel = url.split('/')[2]
      filename = url.split('/')[3]
      outputpath = (basedir + '/' + filename + '.mp4').replace('\n', '')
      print outputpath
      if not os.path.exists(basedir + '/'):
        os.makedirs(basedir + '/')
      print '1'
      html = str(urllib2.urlopen(url).read())
      mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
      urllib.urlretrieve(mp4url, outputpath)
      channel = url.split('/')[2]
      filename = url.split('/')[3]
      outputpath = (basedir + '/' + filename + '.mp4').replace('\n', '')
      fileN = outputpath
      print '2'
      if not os.path.exists(basedir + '/'):
        os.makedirs(basedir + '/')
      title = submission.title
      description = 'Join the discussion on Reddit.\nReddit: ' + submission.url + '\nTwitch Stream: ' + url + '\n\nLike, share and subscribe to our channel for daily League of Legends live gameplay videos!\nHelp us reach 100 subscribers\n\nAll the music and video copyrights are owned by their respective copyright holders.'
      html = str(urllib2.urlopen(url).read())
      mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
      urllib.urlretrieve(mp4url, outputpath)





    argparser.add_argument("--file", help="Video file to upload", default = fileN)
    argparser.add_argument("--title", help="Video title", default=title)
    argparser.add_argument("--description", help="Video description",
    default=description)
    argparser.add_argument("--category", default=category,
      help="Numeric video category. " +
        "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
      default=keywords)
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
      default='private', help="Video privacy status.")
    args = argparser.parse_args()
    print type(args);
    

    youtube = get_authenticated_service(args)
    print('YT tak')
    try:
      initialize_upload(youtube, args)
      print('initialize tak')
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
