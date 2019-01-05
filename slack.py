#!/usr/bin/python
# encoding: utf-8

# license: MIT

# Slack webhook for MotionEyeOS
# adapted from https://github.com/IAmOrion/MotionEyeOS_Add-On_Scripts and https://github.com/ccrisan/motioneyeos/issues/1557
# utilizes https://healthchecks.io as a heartbeat monitor for issuing motion notifications (also integrated into cron)
# Ryan Matthews
# https://github.com/mhaddy
# mhaddy@gmail.com

import config as cv
import pycurl, cStringIO, glob, os, json, pytz, datetime, time

global MESSAGE, FILENAME, FILE_FOUND

WEBHOOK_URL = "https://slack.com/api/files.upload"
WEBHOOK_AUTH_BEAR = "Bearer " + cv.BEARER_TOKEN
WEBHOOK_HEADER = ["Content-Type: multipart/form-data", "Authorization: " + WEBHOOK_AUTH_BEAR]

if cv.DISPLAY_IMAGE:
	# recursively search for the latest image that displays the captured motion
	FIND_LATEST_FILE = 1
else:
	# display the standard 'no image found' with the text cv.INIT_COMMENT
	FILENAME = './No_Image_Available_sm.jpg'

TIMEZONE = os.path.realpath('/data/etc/localtime').replace('/usr/share/zoneinfo/posix/','')

utc = pytz.timezone('UTC')
now = utc.localize(datetime.datetime.utcnow())
la = pytz.timezone(TIMEZONE)
local_time = now.astimezone(la)

CURRENT_TIME = local_time.strftime('%Y-%m-%dT%H:%M:%S.000Z') # UTC Formatted for use in Slack's timestamp argument
MESSAGE_TIME = local_time.strftime(cv.MESSAGE_DATEFORMAT)

def find_latest_file():
	global FILE_FOUND, FILENAME
	FILE_FOUND = 0
	TODAYS_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
	TODAYS_DATE_FOLDER = cv.MEDIA_FOLDER + TODAYS_DATE + '/*.jpg'

	LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER) 
	
	try:
		LATEST_FILE = max(LIST_OF_FILES, key=os.path.getctime)
		FILE_FOUND = 1

	except ValueError:
		FILE_FOUND = 0
	
	if FILE_FOUND:
		FILENAME = LATEST_FILE
	else: 
		FILENAME = '/data/output/noimage.jpg'
		
def send_to_slack():	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, WEBHOOK_URL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPHEADER, WEBHOOK_HEADER)
	c.setopt(c.USERAGENT, cv.USER_AGENT)

	if os.path.isfile(FILENAME):
                c.setopt(c.HTTPPOST, [("initial_comment", cv.INIT_COMMENT + MESSAGE_TIME),("title", cv.CAMERA_NAME),("channels", cv.CHANNEL_ID),("file", (c.FORM_FILE, FILENAME))])
	else:
		c.setopt(c.HTTPPOST, [("initial_comment", cv.INIT_COMMENT + MESSAGE_TIME),])
	
	c.setopt(c.VERBOSE, PYCURL_VERBOSE)
	
	c.perform()
	c.close()
	
	f = buf.getvalue()
	buf.close()
	
	if cv.DEBUG:	
		print(f)
		
print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Running Slack Script... ")
print("================================================================================\n")

if cv.DISPLAY_IMAGE:
	find_latest_file()
	
	print("Finding last captured still image...")
	
send_to_slack()

print("\n================================================================================")
print(" MotionEyeOS - Motion Detected, Discord Script Completed ")
print("================================================================================\n")
