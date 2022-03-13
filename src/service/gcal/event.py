from typing import Dict, Optional, Any
import pprint
import datetime
import dateutil.parser
import dateutil.tz


class Event:
    def __init__(self,
                 service: 'GoogleCalendarService',
                 data: Dict) -> None:
        self.service = service
        self.id = data['id']
        self.status = data['status']  # "confirmed" / "tentative" / "cancelled"
        self.data = data
        self.is_all_day = False
        self.start = None
        self.end = None
        assert data['status'] == "confirmed" \
            or data['status'] == "tentative" \
            or data['status'] == "cancelled"
        assert data['kind'] == "calendar#event"

        if 'dateTime' in data['start']:
            self.start = dateutil.parser.isoparse(data['start']['dateTime'])
            if self.start.tzinfo is None and 'timeZone' in data['start']:
                self.start.tzinfo = self.start.astimezone(
                    dateutil.tz.gettz(data['start']['timeZone']))
        else:
            assert 'date' in data['start']
            self.start = datetime.date.fromisoformat(data['start']['date'])
            self.is_all_day = True

        if 'end' not in data:
            return

        if 'dateTime' in data['start']:
            self.end = dateutil.parser.isoparse(data['end']['dateTime'])
            if self.end.tzinfo is None and 'timeZone' in data['end']:
                self.end.tzinfo = self.end.astimezone(
                    dateutil.tz.gettz(data['end']['timeZone']))
        else:
            assert 'date' in data['end']
            self.end = datetime.date.fromisoformat(data['end']['date'])
            assert self.is_all_day

    def __str__(self) -> str:
        return f"{self.id}: {pprint.pformat(self.data)}"

    def __getitem__(self, name: str) -> Optional[Any]:
        return self.data.get(name)
    
    @property
    def name(self) -> str:
        return self.id

    @property
    def is_deleted(self) -> bool:
        return self.status == "cancelled"
