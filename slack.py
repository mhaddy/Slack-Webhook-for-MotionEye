#!/usr/bin/python
# encoding: utf-8

# license: MIT

# Slack webhook for MotionEyeOS
# adapted from https://github.com/IAmOrion/MotionEyeOS_Add-On_Scripts and https://github.com/ccrisan/motioneyeos/issues/1557
# utilizes https://healthchecks.io as a heartbeat monitor for issuing motion notifications (also integrated into cron)
# Ryan Matthews
# https://github.com/mhaddy
# mhaddy@gmail.com

global MESSAGE, FILENAME, FILE_FOUND

# settings
###############################################
WEBHOOK_URL="https://slack.com/api/files.upload"
WEBHOOK_TITLE = ":warning: Motion Detected!\n\n" # https://api.slack.com/docs/message-formatting
WEBHOOK_CAMERA = "Garage" # change to the name of your camera
WEBHOOK_CHANNELS = "YOUR_CHANNEL_ID" # enclose with [] if multiple channels
WEBHOOK_AUTH_BEAR = "Bearer YOUR_BEARER_TOKEN"
WEBHOOK_HEADER = ["Content-Type: multipart/form-data", "Authorization: "+WEBHOOK_AUTH_BEAR]

OVERRIDE_TIMEZONE = 0 # 1 Override timezone or 0 use MotionEye set timezone
OVERRIDE_TIMEZONE_WITH = "America/Toronto" # Only used is above is set to 1

TIMEZONE = "America/Toronto"
MESSAGE_DATEFORMAT = "%Y/%m/%d @ %I:%M:%S %p" # Date format used in the message itself https://www.tutorialspoint.com/python/time_strftime.htm

NETWORK_SHARE = 1 # Are you using a network share for storage? 1 = yes, 0 = no
SHARE_FOLDER = '/data/output/Camera1/' # Only required if NETWORK_SHARE = 1

if NETWORK_SHARE:
	FIND_LATEST_FILE = 1
else:
	#FILENAME = '/data/output/noimage.jpg'
	#FILENAME = '/data/output/Camera1/lastsnap.jpg'
	FILENAME = '/data/output/Camera1/2018-12-02/18-24-26.jpg'	

PYCURL_VERBOSE = True  # Can be useful for debugging the http post.  True / False

DEBUG = 1 # If set to 1, the response from Discord will be output in terminal.  Useful when testing manually

# ================================================================================
# Do not edit below this line unless you know what you're doing!
# ================================================================================

import pycurl, cStringIO, glob, os, json, pytz, datetime, time

if OVERRIDE_TIMEZONE:
	TIMEZONE = OVERRIDE_TIMEZONE_WITH
else:
	TIMEZONE = os.path.realpath('/data/etc/localtime').replace('/usr/share/zoneinfo/posix/','')

utc = pytz.timezone('UTC')
now = utc.localize(datetime.datetime.utcnow())
la = pytz.timezone(TIMEZONE)
local_time = now.astimezone(la)

CURRENT_TIME = local_time.strftime('%Y-%m-%dT%H:%M:%S.000Z') # UTC Formatted for use in Slack's timestamp argument
MESSAGE_TIME = local_time.strftime(MESSAGE_DATEFORMAT)

# message that appears ahead of the file attachment
# WEBHOOK_CONTENT = { "initial_comment": WEBHOOK_TITLE + MESSAGE_TIME, "title": WEBHOOK_CAMERA }

# don't have to worry about this for now as we're not looking for the latest file
# static file sending above defined as FILENAME = XXX because NETWORK_SHARE = 0
def find_latest_file():
	global FILE_FOUND, FILENAME
	FILE_FOUND = 0
	TODAYS_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
	TODAYS_DATE_FOLDER = SHARE_FOLDER + TODAYS_DATE + '/*.jpg'

	LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER) # * means all, if need specific format then *.jpg (as an example).  Just FYI - MotionEye stores still images as jpg
	
	try:
		LATEST_FILE = max(LIST_OF_FILES, key=os.path.getctime)
		FILE_FOUND = 1

	except ValueError:
		FILE_FOUND = 0
	
	if FILE_FOUND:
		FILENAME = LATEST_FILE
	else: 
		FILENAME = '/data/output/noimage.jpg'
		
def send_to_discord():	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, WEBHOOK_URL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPHEADER, WEBHOOK_HEADER)
	c.setopt(c.USERAGENT, "MotionEyeOS")

	if os.path.isfile(FILENAME):
		# we go through this one because it finds the file
                c.setopt(c.HTTPPOST, [("initial_comment", WEBHOOK_TITLE + MESSAGE_TIME),("title", WEBHOOK_CAMERA),("channels", WEBHOOK_CHANNELS),("file", (c.FORM_FILE, FILENAME))])
#		c.setopt(c.HTTPPOST, [("initial_comment", json.dumps(WEBHOOK_CONTENT)),("channels", WEBHOOK_CHANNELS),("file", (c.FORM_FILE, FILENAME))])
	else:
		c.setopt(c.HTTPPOST, [("initial_comment", json.dumps(WEBHOOK_CONTENT)),])
	
	c.setopt(c.VERBOSE, PYCURL_VERBOSE)
	
	c.perform()
	c.close()
	
	f = buf.getvalue()
	buf.close()
	
	if DEBUG:	
		print(f)
		
print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Running Slack Script... ")
print("================================================================================\n")

if NETWORK_SHARE:

	find_latest_file()
	
	print("Finding last captured still image...")
	
send_to_discord()

print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Discord Script Completed ")
print("================================================================================\n")
