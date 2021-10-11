from discord import user
from google_calendar import GoogleCalendar
from datetime import datetime, timedelta
import asyncio
import pytz
from .pagination import pagination

class Notification:
    client = None
    duration = None

    def __init__(self, client, duration):
        self.client = client
        self.duration = duration

    # Daily message for user
    async def notify_upcomming_event(self, user_id, user_calendar):
        await self.client.wait_until_ready()

        now = datetime.now(pytz.timezone(user_calendar.timezone)) - timedelta(seconds=2)
        upcoming = user_calendar.watch_notification(self.duration)
        index = 0
        for event in upcoming:
            start = datetime.fromisoformat(event['start']['dateTime'])
            if start.date() < now.date() or start.time() < now.time():
                index += 1
            else:
                break

        if len(upcoming) != index:
            upcoming = upcoming[index:]
            format = {
                'title': "Upcoming Event Alert",
                'description':"Here are the upcoming events you have right now.",
                'color':0xfc2c03,
            }
            upcoming = user_calendar.page_divider(upcoming, format)
            await pagination(upcoming, self.client, self.client.get_user(user_id))


    async def check_schedule(self, user_data):
        now = datetime.utcnow()
        user_calendar = GoogleCalendar(user_data["id"])
        # next duration minutes time
        WHEN = now.time()
        if now.second > 0:
            WHEN = (datetime.utcnow()\
                + timedelta(minutes=self.duration-1 - now.minute%self.duration, seconds = 60 - now.second)).time()

        if now.time() < WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
            next_notif = datetime.utcnow() + timedelta(minutes=self.duration-1 - now.minute%self.duration, seconds = 60 - now.second)
            seconds = (next_notif - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
            
        while True:
            now = datetime.utcnow()
            target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
            await self.notify_upcomming_event(user_data["id"], user_calendar)  # Call the helper function that sends the message
            timezone = user_calendar.timezone
            current = datetime.now(pytz.timezone(timezone))
            next_notif = (datetime.now(pytz.timezone(timezone))\
            + timedelta(minutes=self.duration)) \
            .astimezone(pytz.utc).replace(tzinfo=None)
            seconds = (next_notif - now).total_seconds()  # Seconds until duration more minutes (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start