import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich import print
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table

from incredible_data.events.clients.google.auth import get_credentials
from incredible_data.events.clients.google.models import Events
from incredible_data.helpers.functions import truncate_string

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = get_credentials(SCOPES)

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.UTC).isoformat()
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        event_objs = Events.model_validate(events)

        pprint(event_objs[0])

        print(f"Event type: {type(events[0])}")

        console = Console()

        table = Table(title="Events")
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Summary")
        table.add_column("Status")
        table.add_column("Location")
        table.add_column("Description")

        # Prints the start and name of the next 10 events
        for event in event_objs:
            start = f"{event.start.datetime_aware:'%x %X'}"
            end = f"{event.end.datetime_aware}"
            summary = event.summary
            status = event.status
            location = event.location or "n/a"
            description = event.description or "n/a"

            table.add_row(
                start, end, summary, status, location, truncate_string(description)
            )

        console.print(table)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
