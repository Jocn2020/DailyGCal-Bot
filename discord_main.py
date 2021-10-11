import os
from dotenv import load_dotenv
import discord

from google_calendar import GoogleCalendar
import database as db
from features.embedFormat import *
from features.scheduler import DailyScheduler
from features.notifications import Notification
from features.pagination import pagination
import pytz

load_dotenv('./bot-env/pyvenv.cfg')
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
daily_scheduler = DailyScheduler(client)
notifier = Notification(client, 15)

scheduler_task = {}
notifier_task = {}

command_list = {
    "-switch": "ℹ Switch to another account calendar, choose new account and accept all permissions",
    "event": "ℹ Show full data for the selected event in the day\
            \n❗Required: `[event_name]` - Specify the event name",
    "now": "ℹShow current ongoing event from the user calendar",
    "today": "ℹ Show upcoming events schedule",
    "prev": "ℹ Show finished events during the day",
    "notif": "ℹ Enable notification feature \
            \nℹ Upcoming event will be alerted every 15 minutes \
            \n❇Additional: `off` - Turn off the feature",
    "schedule":  "ℹ Enable/disable daily schedule feature \
                \nℹ Full daily schedule will show up at 5 am everyday \
                \n❇Additional: `off` - Turn off the feature",
    "start": "ℹ Create a quick event starting from current time \
            \n❗Required: `[event_name]` - Specify the event name \
            \n❇Additional: `-t [duration]` - Set duration in hours (default = 1 hour)",
    "end": "ℹ Finish current ongoing event, event end time will be set to current time (Doesnt apply for meeting events) \
            \n❗Required: `[event_name]` - Specify the event name",
}

upcoming_command = {
    "set": "ℹ Finish current ongoing event, event end time will be set to current time (Doesnt apply for meeting events) \
            \n❗Required: `[event_name]` - Specify the event name\
            \n❗Follow-Up: `[start] and [end]` - Specify start and end time from range 00:00 - 23:59\
            \n❗Follow-Up: `[recurrence]` - Specify recurrence: daily, weekly, weekday"
}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
            
    for user in db.get_all_user("notifier"):
        notifier_task[user["id"]] = client.loop.create_task(notifier.check_schedule(user))
    for scheduler in db.get_all_user("scheduler"):
        scheduler_task[scheduler["id"]] = client.loop.create_task(daily_scheduler.background_task(scheduler))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if not message.content.startswith('$gcal'):
        return
    
    def message_parser(raw_message):
        result = {}
        split = raw_message.content.split(" ")
        length = len(split)
        command = split[1]
        

        if command != "help" and '-h' in split:
            result['help'] = True
        else:
            result['help'] = False

        result['command'] = command.lower()
        # condition for notif, schedule
        if command == "notif" or command == "schedule":
            if length > 2 and split[2].lower() == "off":
                result["on"] = False
            else:
                result["on"] = True
        
        # Start + duration feature
        if command == "start":
            def isfloat(value):
                decimal = value.split('.')
                if len(decimal) == 2:
                    return decimal[0].isdigit() and decimal[1].isdigit()
                elif len(decimal) == 1:
                    return decimal[0].isdigit()
                else:
                    return False

            if "-t" in split and isfloat(split[split.index("-t")+1]):
                result["event"] = " ".join(split[2: split.index("-t")])
                result["duration"] = float(split[split.index("-t")+1])
            else:
                result["event"] = " ".join(split[2:])
                result["duration"] = 1
        
        # get event title
        if command == "end" or command == "event" or command == "set":
            result["event"] = " ".join(split[2:])
            
        return result

    parsed = message_parser(message)

    if parsed["help"]: # -h feature
        command = parsed['command']
        embedVar = discord.Embed(
            title='⚙ `' + command + '`',
            description=command_list[command],
            color=0xf05ef7
        )
        await message.author.send(embed=embedVar)
        return 0

    if parsed["command"] == "-switch":
        scope = ['https://www.googleapis.com/auth/calendar.readonly', 
                'https://www.googleapis.com/auth/calendar.settings.readonly',
                'https://www.googleapis.com/auth/calendar.events']
        user_calendar = GoogleCalendar(message.author.id).update_creds(None, scope, 'new')
        await message.author.send('🚀New account calendar has been set🚀')

    if parsed["command"] == "help":
        embedVar = discord.Embed(
            title="DailyGCal Command List",
            description="Run the command with the format `$gcal [command_name]`",
            color=0xf05ef7
        )
        for command in command_list.keys():
            embedVar.add_field(
                name='⚙ `' + command + '`',
                value=command_list[command],
                inline=False
            )
        await message.author.send(embed=embedVar)

    if parsed["command"] == "notif":
        user_calendar = GoogleCalendar(message.author.id)
        reply = ""
        notif_on = message.author.id in notifier_task.keys()
        if parsed["on"] == False:
            if notif_on:
                db.remove_user(message.author.id, "notifier")
                notifier_task[message.author.id].cancel()
                notifier_task.pop(message.author.id)
                reply = "⚪Notifier has been set to off⚪"
            else:
                reply = "⚪Notifier is currently off already⚪"
        else:
            if notif_on:
                reply = "💡Notifier is currently on already💡"
            else:
                user_data = {}
                user_data["id"] = message.author.id
                db.store_new_user(user_data, "notifier")
                reply = "💡Notifier is On, Any event within 15 minutes will be notified to the user💡"
                notifier_task[user_data["id"]] = client.loop.create_task(notifier.check_schedule(user_data))
        await message.author.send(reply)

    if parsed["command"] == "schedule":
        user_calendar = GoogleCalendar(message.author.id)
        reply = ""
        schedule_on = message.author.id in scheduler_task.keys()
        if parsed["on"] == False:
            if schedule_on:
                db.remove_user(message.author.id, "scheduler")
                scheduler_task[message.author.id].cancel()
                scheduler_task.pop(message.author.id)
                reply = "⚪Scheduler has been set to off⚪"
            else:
                reply = "⚪Scheduler is currently off already⚪"
        else:
            if schedule_on:
                reply = "💡Scheduler is currently on already💡"
            else:
                user_data = {}
                user_data["id"] = message.author.id
                db.store_new_user(user_data, "scheduler")
                reply = "💡Scheduler is On, daily notification will be conducted everyday at 07:00 AM💡"
                scheduler_task[user_data["id"]] = client.loop.create_task(daily_scheduler.background_task(user_data))
        await message.author.send(reply)
        
    if parsed["command"] == "prev" or parsed["command"] == "today":
        user_calendar = GoogleCalendar(message.author.id)
        today = datetime.datetime.now()
        events = user_calendar.get_schedule(date="past" if parsed["command"].lower() == "prev" else "now")
        format = {
            'title': user_calendar.date_parser.day_date_parser(today),
            'description':"Here are the events you have for today.",
            'color':0x00ff00,
        }
        await pagination(user_calendar.page_divider(events, format), client, message.author)
    
    if parsed["command"] == "now":
        user_calendar = GoogleCalendar(message.author.id)
        today = datetime.datetime.now()
        events = user_calendar.watch_notification(0)
        format = {
            'title': user_calendar.date_parser.day_date_parser(today),
            'description':"Here are the events you currently ongoing.",
            'color':0x00ff00,
        }
        await pagination(user_calendar.page_divider(events, format), client, message.author)

    if parsed["command"] == "start":
        user_calendar = GoogleCalendar(message.author.id)
        event_title = parsed["event"]
        duration = parsed["duration"]
        if event_title == "":
            await message.author.send("Please specify the event (add -h for command help)")
        else:
            ongoings = [event["summary"].lower() if "summary" in event else "" for event in user_calendar.watch_notification(0)]

            if event_title.lower() in ongoings:
                await message.author.send(event_title + " event is currently ongoing (add -h for command help)")
            else:
                current_event = user_calendar.set_quick_event(event_title, duration)
                await message.author.send("Enjoy your "+ current_event["summary"] + " time!")
    
    if parsed["command"] == "end":
        user_calendar = GoogleCalendar(message.author.id)
        event_title = parsed["event"]
        if event_title == "":
            await message.author.send("Please specify the event (add -h for command help)")
        else:
            ongoing_events = user_calendar.watch_notification(0)
            ongoings = [event["summary"].lower() if "summary" in event else "" for event in ongoing_events]
            if event_title.lower() in ongoings:
                current_event = ongoing_events[ongoings.index(event_title.lower())]
                if 'hangoutLink' in current_event:
                    await message.author.send("You can't quick end a meeting event (add -h for command help)")
                    return 0
                now = datetime.datetime.now(pytz.timezone(current_event['start']['timeZone'])).isoformat()
                new_event = user_calendar.update_event(event=current_event, end=now)
                # event current end time
                end = user_calendar.date_parser.result_format(new_event['end'].get('dateTime', new_event['end'].get('date')))
                await message.author.send(new_event['summary'] + " ended now at " + end)
            else:
                await message.author.send(event_title + " event is not currently ongoing (add -h for command help)")
    
    if parsed["command"] == "event":
        user_calendar = GoogleCalendar(message.author.id)
        event_title = parsed["event"]
        if event_title == "":
            await message.author.send("Please specify the event (add -h for command help)")
        else:
            today_events = user_calendar.get_schedule()
            events = [event["summary"].lower() if "summary" in event else "" for event in today_events]
            if event_title.lower() in events:
                current_event = today_events[events.index(event_title.lower())]
                await message.author.send(embed=event_format(current_event))
            else:
                await message.author.send("No such event today (add -h for command help)")


client.run(os.environ.get('TOKEN'))