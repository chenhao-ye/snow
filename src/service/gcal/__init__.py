import os.path
import logging
from collections import OrderedDict
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .calendar import Calendar


class GoogleCalendarService:
    # For now, we only need the readonly permission of Google Calendar.
    # If modifying these scopes, delete the file token file.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    FIELDS = ["cal_name", "title", "time", "location", "description"]

    def __init__(self) -> None:
        self.creds = None
        self.service = None
        self.is_auth = False
        self.cal_map = None

    def auth(self, creds_path: str, token_path: str) -> None:
        """Perform authentications.

        Two files are involved:
        - credentials file: to prove to Google that the current application is AutoFlow.
        - token file: to ask the user to grant the access of the calendar data.
        """
        if self.is_auth:
            return

        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(
                token_path, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('calendar', 'v3', credentials=self.creds)
        self.is_auth = True

    def fetch_calendars(self) -> None:
        assert self.is_auth
        if self.cal_map is not None:
            return

        self.cal_map = OrderedDict()
        # calendar list is broken into multiple pages
        # use page_token to iterate through the pages
        page_token = None
        while True:
            cal_list_page = self.service.calendarList().list(
                pageToken=page_token).execute()
            for cal_data in cal_list_page['items']:
                cal = Calendar(self.service, cal_data)
                self.cal_map[cal.name] = cal
                logging.debug(f"Get calendar: {cal.name}")
            page_token = cal_list_page.get('nextPageToken')
            if not page_token:
                break

    def list_calendars_name(self) -> List[str]:
        """Return all calendars' name of this user."""
        self.fetch_calendars()
        return self.cal_map.keys()

    def get_calendar(self, cal_name: str) -> Optional[Calendar]:
        self.fetch_calendars()
        return self.cal_map.get(cal_name)
