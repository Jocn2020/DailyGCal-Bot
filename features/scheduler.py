from google_calendar import GoogleCalendar
from datetime import datetime, timedelta
import asyncio
import pytz
from .pagination import pagination

class DailyScheduler:
    client = None

    def __init__(self, client):
        self.client = client

    # Daily message for user
    async def daily_scheduler(self, user_id, user_calendar):
        await self.client.wait_until_ready()

        today = datetime.now()
        format = {
            'title':user_calendar.date_parser.day_date_parser(today),
            'description':"Here are the events you have for today.",
            'color':0xf0fc03
        }
        current_task = user_calendar.page_divider(user_calendar.get_schedule(), format)
        await pagination(current_task, self.client, self.client.get_user(user_id))


    async def background_task(self, user_data):
        user_calendar = GoogleCalendar(user_data["id"])
        now = datetime.utcnow()
        WHEN = (datetime.utcnow()+timedelta(seconds = 5)).time() # For testing
        if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
            tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.time(0))
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
        while True:
            now = datetime.utcnow() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
            target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
            await self.daily_scheduler(user_data["id"], user_calendar)  # Call the helper function that sends the message
            timezone = user_calendar.timezone
            current = datetime.now(pytz.timezone(timezone))
            tomorrow = datetime.now(pytz.timezone(timezone))\
            .replace(day=current.day+1, hour=0, minute=0, second=0, microsecond=0) \
            .astimezone(pytz.utc).replace(tzinfo=None)
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start