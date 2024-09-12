"""Google Calendar Event Models."""

from datetime import date as date_type
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import AnyUrl, EmailStr, Field, RootModel, model_validator
from rich.pretty import pprint

from incredible_data.helpers.pydantic import BaseModelCamel


class EventTime(BaseModelCamel):
    date: date_type | None = None
    date_time: datetime | None = None
    time_zone: str | None = None

    @model_validator(mode="after")
    def date_or_datetime(self):
        if self.date is None and self.date_time is None:
            msg = "Either date or dateTime must be present."
            raise ValueError(msg)
        if self.date_time is not None and self.time_zone is None:
            msg = "If dateTime is present, timeZone must be present."
            raise ValueError(msg)
        return self

    @property
    def datetime_aware(self) -> datetime | date_type:
        if self.date is not None:
            return self.date
        assert self.time_zone is not None
        assert self.date_time is not None
        timezone = ZoneInfo(self.time_zone)
        return self.date_time.astimezone(timezone)


class EventUser(BaseModelCamel):
    id: str | None = None
    email: EmailStr
    self: bool | None
    display_name: str | None = None


class EventAttendee(EventUser):
    organizer: bool | None = None
    response_status: str | None = None
    self: bool | None = None


class ReminderOverride(BaseModelCamel):
    method: Literal["email", "popup"]
    minutes: int = Field(..., ge=0, le=40320)


class Reminder(BaseModelCamel):
    use_default: bool = True
    overrides: list[ReminderOverride] | None = None


class Location(BaseModelCamel):
    address: str


class Event(BaseModelCamel):
    etag: str | None = None
    id: str | None = None
    status: str | None = None
    html_link: AnyUrl | None = None
    created: datetime | None = None
    updated: datetime | None = None
    summary: str
    creator: EventUser | None = None
    organizer: EventUser | None = None
    start: EventTime
    end: EventTime
    end_time_unspecified: bool | None = None
    reccurence: list[str] | None = None
    recurring_event_id: str | None = None
    original_start_time: EventTime | None = None
    i_cal_uid: str | None = Field(default=None, alias="iCalUID")
    sequence: int | None = None
    attendees: list[EventAttendee] = []
    guests_can_modify: bool = False
    reminders: Reminder = Reminder()
    event_type: Literal[
        "birthday",
        "default",
        "focusTime",
        "fromGmail",
        "outOfOffice",
        "workingLocation",
    ] = "default"
    location: str | None = None
    description: str | None = None
    color_id: str | None = None


class Events(RootModel):
    root: list[Event]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index) -> Event:
        return self.root[index]


class NewEvent(BaseModelCamel):
    summary: str
    location: str = ""
    description: str = ""
    start: EventTime
    end: EventTime


if __name__ == "__main__":
    event_dict = {
        "kind": "calendar#event",
        "etag": '"3408854086220000"',
        "id": "003e526tbd6h5093v2i84gc241_20240917T030000Z",
        "status": "confirmed",
        "htmlLink": "https://www.google.com/calendar/event?eid=MDAzZTUyNnRiZDZoNTA5M3YyaTg0Z2MyNDFfMjAyNDA5MTdUMDMwMDAwWiBrYXJsd29vc3RlckBt",
        "created": "2024-01-05T03:57:23.000Z",
        "updated": "2024-01-05T03:57:23.110Z",
        "summary": "Budget Meeting",
        "creator": {"email": "karlwooster@gmail.com", "self": True},
        "organizer": {"email": "karlwooster@gmail.com", "self": True},
        "start": {
            "dateTime": "2024-09-16T20:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": "2024-09-16T20:30:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "recurringEventId": "003e526tbd6h5093v2i84gc241",
        "originalStartTime": {
            "dateTime": "2024-09-16T20:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "iCalUID": "003e526tbd6h5093v2i84gc241@google.com",
        "sequence": 0,
        "attendees": [
            {
                "email": "karlwooster@gmail.com",
                "organizer": True,
                "self": True,
                "responseStatus": "accepted",
            },
            {"email": "samlsanderson@gmail.com", "responseStatus": "needsAction"},
        ],
        "guestsCanModify": True,
        "reminders": {
            "useDefault": False,
            "overrides": [{"method": "popup", "minutes": 480}],
        },
        "eventType": "default",
    }

    event = Event.model_validate(event_dict)

    pprint(event)
