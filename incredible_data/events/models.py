import datetime as dt

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rubble.models.history_models import HistoryModel
from humanize import ordinal

# Create your models here.


class Event(HistoryModel):
    description = models.TextField()
    location = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return self.title


# region Google Models
class GoogleUser(models.Model):  # type: ignore[django-manager-missing]
    email = models.EmailField()
    display_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.display_name if self.display_name != "" else self.email


class GoogleEvent(Event):
    google_id = models.CharField(max_length=255, editable=False, unique=True)
    google_calendar_id = models.CharField(max_length=255)
    google_html_link = models.URLField()
    google_status = models.CharField(max_length=255)
    google_created = models.DateTimeField()
    google_updated = models.DateTimeField()
    google_creator = models.ForeignKey(
        GoogleUser,
        verbose_name=_("creator"),
        on_delete=models.PROTECT,
        related_name="creator",
    )
    google_organizer = models.ForeignKey(
        GoogleUser,
        verbose_name=_("organizer"),
        on_delete=models.PROTECT,
        related_name="organizer",
    )
    google_end_time_unspecified = models.BooleanField()
    google_reccurence = models.JSONField()
    google_recurring_event_id = models.CharField(max_length=255)
    google_original_start_time = models.DateTimeField()
    google_i_cal_uid = models.CharField(max_length=255, editable=False)
    google_sequence = models.IntegerField()
    google_attendees = models.ManyToManyField(
        GoogleUser, verbose_name=_("attendees"), through="GoogleAttendees"
    )  # type: ignore[var-annotated]
    google_guests_can_modify = models.BooleanField()
    google_reminders = models.JSONField()
    google_event_type = models.CharField(max_length=255)
    google_color_id = models.CharField(max_length=255)


class GoogleAttendees(models.Model):
    google_event = models.ForeignKey(GoogleEvent, on_delete=models.CASCADE)
    google_user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE)
    google_organizer = models.BooleanField()
    google_response_status = models.CharField(max_length=255)
    google_self = models.BooleanField()

    def __str__(self):
        return f"{self.google_user} is attending {self.google_event}"


# endregion Google Models
def event_age(*, current_date: dt.datetime, start_date: dt.datetime | dt.date) -> int:
    """Calculate the age of an event.

    Examples:

    Args:
        current_date (datetime): The current date.
        start_date (datetime): The date of the event.

    Returns:
        int: The age of the event.
    """
    return current_date.year - start_date.year


class Anniversary(HistoryModel):
    start_date = models.DateField(
        _("start date"),
        help_text=_("The original date of the event; e.g. birthday or wedding."),
    )
    year_known = models.BooleanField(
        _("year known"),
        help_text=_("Whether the year of the event is known or not."),
        default=True,
    )
    EVENT_TYPE_CHOICES = [
        ("birthday", _("Birthday")),
        ("wedding", _("Wedding")),
        ("other", _("Other")),
    ]
    event_type = models.CharField(
        _("event type"), choices=EVENT_TYPE_CHOICES, max_length=25, default="birthday"
    )
    title = models.CharField(
        _("title"),
        help_text=_("base text for event titles, to be used in a possessive"),
        max_length=100,
    )
    back_date = models.BooleanField(_("add past events"), default=False)
    future_events = models.IntegerField(
        _("number of future events to generate"), default=10
    )

    def __str__(self):
        return f"{self.title} Anniversary"

    def event_title(
        self, event_date: dt.datetime, *, event_type: str | None = None
    ) -> str:
        """Generate the title of the event.

        Args:
            event_date (datetime): The date of the event.

        Returns:
            str: The title of the event.
        """
        event_type = self.event_type if event_type is None else event_type
        if self.year_known:
            age = event_age(current_date=event_date, start_date=self.start_date)
            age_ordinal = ordinal(age)
            return f"{self.title}'s {age_ordinal} {event_type.title()}"
        return f"{self.title}'s {event_type.title()}"

    def event_date_for_year(self, year: int):
        """Get the event date for a given year.

        Args:
            year (int): The year to get the event date for.

        Returns:
            datetime: The event date.
        """
        return self.start_date.replace(year=year)

    def generate_events(self):
        """Generate the events for the anniversary."""
        current_date = dt.datetime.now(tz=dt.UTC)
        if self.back_date:
            start_year = self.start_date.year
        else:
            current_year_date = self.event_date_for_year(current_date.year)
            if current_year_date < current_date:
                start_year = current_date.year + 1
            else:
                start_year = current_date.year

        future_event_count = 0
        current_calculate_year = start_year

        while future_event_count < self.future_events:
            event_date = self.event_date_for_year(current_calculate_year)
            title = self.event_title(event_date)
            GoogleEvent.objects.create(
                title=title,
                description=self.title,
                location="",
                start=event_date,
                end=event_date,
            )
            if event_date > current_date:
                future_event_count += 1
            current_calculate_year += 1
