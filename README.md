# Slack-Webhook-for-MotionEye
Add-on script for MotionEye/OS that enables motion notifications on Slack.

Detailed instructions coming later.
1. Clone this repo into your \data directory.
2. Rename config.py.EXAMPLE to config.py.
3. Modify the following variables (at a minimum) per your details:
a. CHANNEL_ID
b. BEARER_TOKEN
4. Within your MotionEye/OS web front-end, login with your admin account and configure the camera you'd like to ensure notifications on.
5. Scroll to the bottom until you see Motion Notifications (you must first ensure Motion Detection is on).
6. Toggle to 'on' the 'Run an End Command' and enter the following:
```
python /data/{name of repo}/slack.py &
```
7. Hit save! You should now receive notifications in your designated Slack channel upon every motion notification with the snapshot image of the motion detection.

### Future Updates/TODO
1. Include a link to the video (if captured)

### Cronjob Health Checks
Ensure your MotionEye/OS system is online by registering for a free account on https://www.healthchecks.io and setting up a monitor. Then create a cron job with the following configuration:
```
crontab -e
```
Then type in the following:
```
0 * * * * {user} curl -fsS --retry 3 https://hc-ping.com/{hash} > /dev/null
```
