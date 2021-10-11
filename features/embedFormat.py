import discord
import datetime

def result_format(date, type="time"):
        parsed = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S-%f:00')
        if type == "time":
            new_date = ("0" if parsed.hour < 10 else "") + str(parsed.hour) + ":" + ("0" if parsed.minute < 10 else "") + str(parsed.minute)
        elif type == "year":
            new_date = ("0" if parsed.hour < 10 else "") + str(parsed.year) + "-" + str(parsed.month) + "-" + str(parsed.day)
        return new_date

def schedule_format(events, num_pages, show_meeting=False):
    embedVar = discord.Embed(
            title='📅 ' + events['title'] + ' 📅',
            description='🏷' + events['description'] +
            ('\n📕Page: `' + str(events['page']) + '/' + str(num_pages) +'`'),
            color=events['color']
        )
    index = events['page']*5 - 5 + 1
    for event in events['schedule']:
        start = result_format(event['start'].get('dateTime', event['start'].get('date')))
        end = result_format(event['end'].get('dateTime', event['end'].get('date')))
        name = "{0}. ".format(str(index)) +  (event["summary"] if "summary" in event.keys() else "(No Title)") \
            + (' 🗓️' if 'hangoutLink' in event else '')
        meeting_schedule = '\n Meeting: ' + event['hangoutLink'] if show_meeting else ''
        embedVar.add_field(name= name, value= "⏰ From `" + start + "` to: `" + end +'`' + meeting_schedule\
            , inline=False) 
        index+= 1
    if index == 1: # no events
        embedVar.add_field(name="(Empty Event)", value="You currently have no event", inline=False)
    return embedVar

def event_format(event):
    start = result_format(event['start'].get('dateTime', event['start'].get('date')))
    end = result_format(event['end'].get('dateTime', event['end'].get('date')))
    meeting = 'hangoutLink' in event
    embedVar = discord.Embed(
        title=event["summary"] if "summary" in event else "(No Title)",
        description="from `" + start + "` to: `" + end + "`",
        color=0x2803fc if meeting else 0x03f0fc
        )
    embedVar.add_field(name="Description:", value=event['description'] if "description" in event else "(No Description)",\
          inline=False)
    # Add meeting link if its exist:
    if 'hangoutLink' in event:
        embedVar.add_field(name="Meeting Url:", value=event['hangoutLink'] , inline=False)
    # Add url to event
    embedVar.add_field(name='Calendar Url:', value=event['htmlLink'] , inline=False)
    return embedVar