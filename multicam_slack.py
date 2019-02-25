#!/usr/bin/python
# encoding: utf-8

# license: MIT

# Multi-cam Slack webhook for MotionEyeOS
# adapted from https://github.com/IAmOrion/MotionEyeOS_Add-On_Scripts with inspiration from:
# - https://github.com/ccrisan/motioneyeos/issues/1557
# - https://github.com/kabadisha/motioneyeos-discord-notifier

# USAGE
# python /{absolute-path-to-your-motion-install}/data/Slack-Webhook-for-MotionEye/multicam_slack.py -n "Garage" -p %f -q %q -v %v &

# Ryan Matthews
# https://github.com/mhaddy
# mhaddy@gmail.com

import config as cv
import pycurl, cStringIO, glob, os, json, pytz, datetime, time
import logging, argparse
from tzlocal import get_localzone
from argparse import RawDescriptionHelpFormatter

global FILENAME, FILE_FOUND

# change logging.INFO to logging.DEBUG at the end of this line
# if you're experiencing issues or need help during initial setup
logging.basicConfig(filename=cv.LOG_DIR+cv.LOG_FILENAME,format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)

WEBHOOK_URL = "https://slack.com/api/files.upload"
WEBHOOK_AUTH_BEAR = "Bearer " + cv.BEARER_TOKEN
WEBHOOK_HEADER = ["Content-Type: multipart/form-data", "Authorization: " + WEBHOOK_AUTH_BEAR]

if cv.DISPLAY_IMAGE:
	# recursively search for the latest image that displays the captured motion
	FIND_LATEST_FILE = 1
else:
	# display the standard 'no image found' with the text cv.INIT_COMMENT
	FILENAME = './No_Image_Available_sm.jpg'

# get local timezone
local_tz = get_localzone()
logging.debug("Local TZ {}".format(local_tz))

# utc_now, now = datetime.utcnow(), datetime.now()
ts = time.time()
utc_now, now = datetime.datetime.utcfromtimestamp(ts), datetime.datetime.fromtimestamp(ts)

local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz) # utc -> local
logging.debug("Local now {}".format(local_now))
assert local_now.replace(tzinfo=None) == now

CURRENT_TIME = local_now.strftime('%Y-%m-%dT%H:%M:%S.000Z') # UTC Formatted for use in Slack's timestamp argument
MESSAGE_TIME = local_now.strftime(cv.MESSAGE_DATEFORMAT)

# get details of the camera, path, and others from the call 
parser = argparse.ArgumentParser(description="Multi-cam Slack notification webhook for MotionEye",epilog="Written by Mhaddy, inspired by IAmOrion and Kabadisha, https://www.github.com/mhaddy", formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("-n", "--cameraname", help="Camera name (something short and description, like Porch)", type=str, default="Camera")
parser.add_argument("-p", "--mediadir", help="Absolute path to the media directory (with trailing slash)", type=str, default="/home/pi/motioneye/media/Camera1/")
parser.add_argument("-q", "--frame", help="%%q option from MotionEye (frame number); used in debug log file", type=int)
parser.add_argument("-v", "--eventnumber", help="%%v option from MotionEye; used in debug log file", type=int)
args = parser.parse_args();

logging.debug("arparse debug | n {} | p {} | q {} | v {}".format(args.cameraname, args.mediadir, args.frame, args.eventnumber))

def find_latest_file(args):
	global FILE_FOUND, FILENAME
	FILE_FOUND = 0
	TODAYS_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
	TODAYS_DATE_FOLDER = args.mediadir + TODAYS_DATE + '/*.jpg'
	logging.debug("Today's Date {}, Date Folder {}".format(TODAYS_DATE,TODAYS_DATE_FOLDER))

	LIST_OF_FILES = glob.glob(TODAYS_DATE_FOLDER)

	try:
		LATEST_FILE = max(LIST_OF_FILES, key=os.path.getctime)
		FILE_FOUND = 1
		logging.debug(LATEST_FILE)

	except ValueError:
		FILE_FOUND = 0

	if FILE_FOUND:
		FILENAME = LATEST_FILE
	else:
		logging.debug("No file found when searching")
		FILENAME = './No_Image_Available_sm.jpg'

def send_to_slack(args):
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, WEBHOOK_URL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.HTTPHEADER, WEBHOOK_HEADER)
	c.setopt(c.USERAGENT, cv.USER_AGENT)

	if os.path.isfile(FILENAME):
		logging.debug("File found {}".format(FILENAME))
                c.setopt(c.HTTPPOST, [("initial_comment", cv.INIT_COMMENT.format(args.cameraname) + MESSAGE_TIME),("title", args.cameraname),("channels", cv.CHANNEL_ID),("file", (c.FORM_FILE, FILENAME))])
	else:
		logging.debug("File not found".format(FILENAME))
		c.setopt(c.HTTPPOST, [("initial_comment", cv.INIT_COMMENT + MESSAGE_TIME),("channels", cv.CHANNEL_ID),])

	c.setopt(c.VERBOSE, cv.PYCURL_VERBOSE)

	c.perform()
	c.close()

	f = buf.getvalue()
	buf.close()

	if cv.DEBUG:
		logging.debug(f)

logging.info("Motion detected on {}".format(cv.CAMERA_NAME))
logging.debug("Frame number: {}".format(args.frame))
logging.debug("Event number: {}".format(args.eventnumber))

# retrieve the latest image and use in the webhook below, if configured in config.py
if cv.DISPLAY_IMAGE:
	logging.debug("Finding last captured still image...")
	find_latest_file(args)

# send motion notification to Slack
send_to_slack(args)
