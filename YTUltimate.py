import urllib2
import urllib
import os
import praw
from time import sleep
from random import randint
import re

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
		html = str(urllib2.urlopen(url).read())
		mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
		urllib.urlretrieve(mp4url, outputpath)
		channel = url.split('/')[2]
		filename = url.split('/')[3]
		outputpath = (basedir + '/' + filename + '.mp4').replace('\n', '')
		if not os.path.exists(basedir + '/'):
			os.makedirs(basedir + '/')
		html = str(urllib2.urlopen(url).read())
		mp4url = html.split('source\":\"')[1].split(',')[0].replace('\"', '')
		urllib.urlretrieve(mp4url, outputpath)
		cmd = 'py LOL\upload_video.py ' + '--file="' + outputpath + '" --title="' + submission.title + '" --description="Join the discussion on Reddit.^\nReddit: ' + submission.url + '^\nTwitch: ' + url + '\n\nLike, share and subscribe to our channel for daily League of Legends live gameplay videos!^\nHelp us reach 100 subscribers^\n^\nAll the music and video copyrights are owned by their respective copyright holders.' '" --privacyStatus="public"' + ' --category="20"' + ' --keywords="league of legends gameplay,league of legends live,league of legends 2017,league of legends funny,league of legends,league of legends game,league of legends new,league of legends latest"'
		print cmd
		break
	
	
