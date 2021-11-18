Daily Gcal Bot
Personal Discord bot to help people to not forget their time when using discord. By using Google Calendar API, user can access their calendar and modify 
current activity so the user will have their daily activity record. In addition, Daily Gcal bot has notification features to give reminder if some event will start
within 5 minutes.

DailyGCal Frameworks:
1. Discord Python
2. Google Calendar API
3. Python Flask (For authentication, currently ongoing)
4. MongoDB 

DailyGCal Command List and Features
Run the command with the format $gcal [command_name]
⚙ -acc
ℹ Register or switch to another account calendar, choose new account and accept all permissions
❗Warning: Currently not working for mobile/ios discord
⚙ event
ℹ Show full data for the selected event in the day
❗Required: [event_name] - Specify the event name
⚙ now
ℹShow current ongoing event from the user calendar
⚙ today
ℹ Show upcoming events schedule
⚙ prev
ℹ Show finished events during the day
⚙ notif
ℹ Enable notification feature
ℹ Upcoming event will be alerted every 15 minutes
❇Additional: off - Turn off the feature
⚙ schedule
ℹ Enable/disable daily schedule feature
ℹ Full daily schedule will show up at 5 am everyday
❇Additional: off - Turn off the feature
⚙ start
ℹ Create a quick event starting from current time
❗Required: [event_name] - Specify the event name
❇Additional: -t [duration] - Set duration in hours (default = 1 hour)
⚙ end
ℹ Finish current ongoing event, event end time will be set to current time (Doesnt apply for meeting events)
❗Required: [event_name] - Specify the event name
⚙ set
ℹ Set your own schedule on Google calendar from the provided url
