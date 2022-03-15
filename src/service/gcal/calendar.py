import pprint
from typing import Dict, Any, Optional
import logging
import datetime

from .event import Event


class Calendar:
    def __init__(self,
                 service: 'GoogleCalendarService',
                 data: Dict) -> None:
        self.service = service
        self.id = data['id']
        self.summary = data['summaryOverride'] if 'summaryOverride' in data else data['summary']
        self.data = data
        self.events_cache = {}

    def __str__(self) -> str:
        return f"{self.id}: {pprint.pformat(self.data)}"

    def __getitem__(self, name: str) -> Optional[Any]:
        return self.data.get(name)

    @property
    def name(self) -> str:
        return self.summary

    def list_events_id(self,
                       *,
                       time_min: Optional[datetime.datetime] = None,
                       sync_token: Optional[str] = None):
        """Return all events within a given calendar."""
        # these two fields cannot be provided together
        assert time_min is None or sync_token is None
        events_id_list = []
        page_token = None
        next_sync_token = None
        while True:
            events_page = self.service.events().list(
                calendarId=self.id,
                pageToken=page_token,
                syncToken=sync_token,
                timeMin=time_min.isoformat() if time_min is not None else None,
                singleEvents='true',
                showDeleted='true').execute()
            for event_data in events_page['items']:
                event = Event(self.service, event_data)
                self.events_cache[event.id] = event
                events_id_list.append(event.id)
                logging.info(f"Get event: {event.name}")
            page_token = events_page.get('nextPageToken')
            if not page_token:
                next_sync_token = events_page.get('nextSyncToken')
                break
        return events_id_list, next_sync_token

    def get_event(self, event_id: str) -> Event:
        if event_id in self.events_cache:
            return self.events_cache[event_id]

        logging.warning(
            f"Event {event_id} not found in the local cache; will query servers")
        event_data = self.service.events().get(
            calendarId=self.id, eventId=event_id).execute()
        event = Event(self.service, event_data)
        self.events_cache[event.id] = event
        logging.info(f"Get event: {event.name}")
        return event
