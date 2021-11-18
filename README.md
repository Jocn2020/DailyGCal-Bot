Daily Gcal Bot <br />
Personal Discord bot to help people to not forget their time when using discord. By using Google Calendar API, user can access their calendar and modify 
current activity so the user will have their daily activity record. In addition, Daily Gcal bot has notification features to give reminder if some event will start within 5 minutes. <br />

DailyGCal Frameworks: <br />
1. Discord Python <br />
2. Google Calendar API <br />
3. Python Flask (For authentication, currently ongoing) <br />
4. MongoDB <br />

DailyGCal Command List and Features:<br />
Run the command with the format $gcal [command_name]<br />
⚙ -acc<br />
ℹ Register or switch to another account calendar, choose new account and accept all permissions<br />
❗Warning: Currently not working for mobile/ios discord<br />
⚙ event <br />
ℹ Show full data for the selected event in the day<br />
❗Required: [event_name] - Specify the event name<br />
⚙ now<br />
ℹShow current ongoing event from the user calendar<br />
⚙ today<br />
ℹ Show upcoming events schedule<br />
⚙ prev<br />
ℹ Show finished events during the day<br />
⚙ notif<br />
ℹ Enable notification feature<br />
ℹ Upcoming event will be alerted every 15 minutes<br />
❇Additional: off - Turn off the feature<br />
⚙ schedule<br />
ℹ Enable/disable daily schedule feature<br />
ℹ Full daily schedule will show up at 5 am everyday<br />
❇Additional: off - Turn off the feature<br />
⚙ start<br />
ℹ Create a quick event starting from current time<br />
❗Required: [event_name] - Specify the event name<br />
❇Additional: -t [duration] - Set duration in hours (default = 1 hour)<br />
⚙ end<br />
ℹ Finish current ongoing event, event end time will be set to current time (Doesnt apply for meeting events)<br />
❗Required: [event_name] - Specify the event name<br />
⚙ set<br />
ℹ Set your own schedule on Google calendar from the provided url<br />
