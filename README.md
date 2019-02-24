# Slack-Webhook-for-MotionEye
Add-on script for MotionEye/OS that enables motion notifications on Slack. Displays an image of the most recently captured motion in a channel of your choice using [Slack's OAuth API](https://api.slack.com/docs/oauth).

:boom: Now with multi-camera support with just one file thanks to some excellent argparse from [Kabadisha](https://github.com/kabadisha/motioneyeos-discord-notifier). Originally inspired by [IAmOrion](https://github.com/IAmOrion/MotionEyeOS_Add-On_Scripts).

Detailed instructions coming later.
1. Clone this repo into your /data directory of your [Motion install](https://github.com/ccrisan/motioneye).
2. Rename config.py.EXAMPLE to config.py.
3. Modify the following variables (at a minimum) in config.py per your details:

   a. CHANNEL_ID (Find this in the URL of your channel, e.g., https://{team-id}.slack.com/messages/{CHANNEL_ID}
   
   b. BEARER_TOKEN (Get your OAUTH access token [here](https://api.slack.com/docs/oauth)
   
   c. LOG_DIR (location of log file)

4. Within your MotionEye/OS web front-end, login with your admin account and configure the camera you'd like to configure notifications for.
5. Scroll to the bottom until you see Motion Notifications (you must first ensure Motion Detection is on).
6. Toggle to 'on' the 'Run an End Command' (so a notification is only triggered at the end of a motion occurrence) and enter the following, replacing -n "Garage" with the name of your camera:
```
# python /{absolute-path-to-your-motion-install}/data/Slack-Webhook-for-MotionEye/multicam_slack.py -n "Garage" -p %f -q %q -v %v &
```
7. Hit save! You should now receive notifications in your designated Slack channel upon every motion notification with the snapshot image of the motion detection.

### Future Updates/TODO
1. Include a link to the video (if captured)

### Cronjob Health Checks
Ensure your MotionEye/OS system is online by registering for a free account on https://www.healthchecks.io and setting up a heart beat monitor (you can also use other services like cronitor.io). Then open your crontab editor:
```
crontab -e
```
Then type in the following to check every 60 mins whether your Pi is online:
```
*/60 * * * * curl -fsS --retry 3 https://hc-ping.com/{hash} > /dev/null
```
