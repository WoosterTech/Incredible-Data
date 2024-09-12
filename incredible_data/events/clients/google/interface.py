import datetime
from zoneinfo import ZoneInfo

from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from rich import print
from rich.pretty import pprint

from incredible_data.events.clients.google.auth import get_credentials
from incredible_data.events.clients.google.models import Event
from incredible_data.events.quickstart import SCOPES


def insert_event(service: Resource, event: Event) -> Event:
    """Insert an event into the Google Calendar.

    Args:
        service: The Google Calendar service.
        event: The event to insert.

    Returns:
        The inserted event.
    """

    event_dict = (
        service.events()
        .insert(calendarId="primary", body=event.model_dump_json(exclude_none=True))
        .execute()
    )

    return Event.model_validate(event_dict)


if __name__ == "__main__":
    time_zone = ZoneInfo("America/Los_Angeles")
    start_dt = datetime.datetime(2024, 9, 13, 8, 0, 0, tzinfo=time_zone)
    end_dt = start_dt + datetime.timedelta(hours=1)
    event_dict = {
        "summary": "Test Event",
        "description": "This is a test event.",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        "attendees": [],
    }
    event_obj = Event.model_validate(event_dict)

    creds = get_credentials(SCOPES)

    try:
        service = build("calendar", "v3", credentials=creds)
        created_event_dict = (
            service.events().insert(calendarId="primary", body=event_dict).execute()
        )
        created_event = Event.model_validate(created_event_dict)

        pprint(created_event)

    except HttpError as error:
        print(f"An error occurred: {error}")
