from __future__ import print_function
import calendar
import datetime
from google.auth import credentials
from pymongo.message import update
import pytz
from math import ceil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import database as db
import json
# If modifying these scopes, delete the file token.json.

class DateParser():
    timezone = None

    def __init__(self, timeZone):
        self.timezone = timeZone

    def result_format(self, date, type="time"):
        parsed = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S-%f:00')
        if type == "time":
            new_date = ("0" if parsed.hour < 10 else "") + str(parsed.hour) + ":" + ("0" if parsed.minute < 10 else "") + str(parsed.minute)
        elif type == "year":
            new_date = ("0" if parsed.hour < 10 else "") + str(parsed.year) + "-" + str(parsed.month) + "-" + str(parsed.day)
        return new_date

    def get_utc_midnight_time(self, index):
        current = datetime.datetime.now(pytz.timezone(self.timezone))
        return datetime.datetime.now(pytz.timezone(self.timezone)) \
                .replace(day=current.day+index, hour=0, minute=0, second=0, microsecond=0) \
                .astimezone(pytz.utc).replace(tzinfo=None).isoformat() + 'Z'

    def day_date_parser(self, date):
        formatted_date = calendar.day_name[date.weekday()] + ", " + calendar.month_name[date.month] + " " + str(date.day) + ", " + str(date.year)
        return formatted_date
    

class GoogleCalendar():
    user_id = None
    service = None
    timezone = None
    date_parser = None

    def __init__(self, user_id):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.user_id = user_id
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 
                'https://www.googleapis.com/auth/calendar.settings.readonly']
        # Update credentials for given condition

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if db.get_user_cred(user_id, "main"):
            cred_dict = json.loads(db.get_user_cred(user_id, "main")["cred"])
            SCOPES = cred_dict["scopes"]
            creds = Credentials.from_authorized_user_info(cred_dict, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.update_creds(creds, SCOPES, "refresh")
            else:
                self.update_creds(creds, SCOPES, "new")
            # Save the credentials for the next run
        self.service = build('calendar', 'v3', credentials=creds)
        self.timezone = self.service.settings().get(setting='timezone').execute()['value']
        self.date_parser = DateParser(self.timezone)

    def page_divider(self, events, format):
        pages = []
        today = datetime.datetime.now()
        num_pages = ceil(len(events)/5) if events != [] else 1
        for page in range(num_pages-1):
            pages.append(
            {
                'title':format['title'],
                'description':format['description'],
                'color':format['color'],
                'page': page+1,
                'schedule': events[page*5:page*5+5]
            })
        # add the remaining data
        if num_pages%5 != 0:
            pages.append(
                {
                    'title':format['title'],
                    'description':format['description'],
                    'color':format['color'],
                    'page': num_pages,
                    'schedule': events[num_pages*5-5:]
                })
        return pages

    def update_creds(self, creds, SCOPES, command):
        if command == "refresh":
            creds.refresh(Request())
        elif command == "new":
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        new_user = {}
        new_user["id"] = self.user_id
        new_user["cred"] = creds.to_json()
        new_user["scopes"] = SCOPES
        db.store_new_user(new_user, "main")

    def update_scopes(self, new_scope):
        creds = None
        self.update_creds(creds, new_scope, "new")

        # Set everything back
        self.service = build('calendar', 'v3', credentials=creds)
        self.timezone = self.service.settings().get(setting='timezone').execute()['value']
        self.date_parser = DateParser(self.timezone)

    def get_schedule(self, date="today"):
        # Call the Calendar API
        schedule = []
        if date == "now" : 
            start_time = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        else:
            start_time = self.date_parser.get_utc_midnight_time(0)

        if date == "past":
            end_time = datetime.datetime.utcnow().isoformat() + 'Z'
        else:
            end_time = self.date_parser.get_utc_midnight_time(1)

        events_result = self.service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time,
                                            timeZone=self.timezone, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            schedule.append(event)
        
        return schedule

    def watch_notification(self, range):
        upcomming_event = []
        start_time = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        end_time = (datetime.datetime.utcnow()+datetime.timedelta(minutes = range+1)).isoformat() + 'Z'
        events_result =self.service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time,
                                            timeZone=self.timezone, maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            upcomming_event.append(event)
        
        return upcomming_event

    def set_quick_event(self, event_title, duration=1):
        # check if credentials already satisfied
        curr_user = db.get_user_cred(self.user_id, 'main')
        scope = 'https://www.googleapis.com/auth/calendar.events'
        if scope not in curr_user["scopes"]:
            curr_user["scopes"].append(scope)
            self.update_scopes(curr_user["scopes"])
        # Quick add the new event
        event = {
            'summary': event_title,
            'start': {
                'dateTime': datetime.datetime.now(pytz.timezone(self.timezone)).isoformat(),
                'timeZone': self.timezone
            },
            'end': {
                'dateTime': (datetime.datetime.now(pytz.timezone(self.timezone)) + datetime.timedelta(hours=duration)).isoformat(),
                'timeZone': self.timezone
            }
        }
        created_event = self.service.events().insert(
                        calendarId='primary',
                        body=event).execute()
        return created_event
        
    def update_event(self, event, start = None, end = None):
        # check if user already have the scope
        curr_user = db.get_user_cred(self.user_id, 'main')
        scope = 'https://www.googleapis.com/auth/calendar.events'
        if scope not in curr_user["scopes"]:
            curr_user["scopes"].append(scope)
            self.add_new_scopes(curr_user["scopes"])

        # start and end time are in utc
        if start:
            event['start']['dateTime'] = start
        if end:
            event['end']['dateTime'] = end

        updated_event = self.service.events()\
                        .update(calendarId='primary', eventId=event['id'], body=event).execute()
        return updated_event