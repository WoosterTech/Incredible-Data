import datetime as dt
from typing import Literal, TypeAlias, overload

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeRangeChoice(models.TextChoices):
    """Time range choices for date filtering."""

    TODAY = "today", _("Today")
    THIS_WEEK = "this_week", _("This Week")
    THIS_MONTH = "this_month", _("This Month")
    LAST_WEEK = "last_week", _("Last Week")
    LAST_7_DAYS = "last_7_days", _("Last 7 Days")
    LAST_30_DAYS = "last_30_days", _("Last 30 Days")
    LAST_MONTH = "last_month", _("Last Month")
    CUSTOM = "custom"


_DateLike: TypeAlias = dt.date | dt.datetime


def get_weekday_int(
    date: _DateLike,
    *,
    week_starts_on: Literal["monday", "sunday"] = "sunday",
) -> int:
    """Get the weekday as an integer (1=Monday, 7=Sunday).

    Args:
        date: The date to get the weekday for.
        week_starts_on: The day the week starts on (either "monday" or "sunday").

    Returns:
        The weekday as an integer (1=Monday, 7=Sunday).
    """
    weekday = date.weekday()
    if week_starts_on == "sunday":
        weekday = (weekday + 1) % 7
    return weekday


@overload
def get_dates(
    period: Literal[None] = None, *, force_date: bool = ...
) -> tuple[None, None]: ...
@overload
def get_dates(
    period: TimeRangeChoice, *, force_date: Literal[False] = False
) -> tuple[_DateLike | None, _DateLike | None]: ...
@overload
def get_dates(
    period: TimeRangeChoice, *, force_date: Literal[True]
) -> tuple[dt.date | None, dt.date | None]: ...
def get_dates(
    period: TimeRangeChoice | None = None, *, force_date: bool = False
) -> tuple[_DateLike | None, _DateLike | None]:
    now = timezone.now()
    start_date = now
    end_date = now
    weekday_int = get_weekday_int(now)

    match period:
        case TimeRangeChoice.TODAY:
            start_date = end_date
        case TimeRangeChoice.THIS_WEEK:
            start_date = now - dt.timedelta(days=weekday_int)
        case TimeRangeChoice.THIS_MONTH:
            start_date = now.replace(day=1)
        case TimeRangeChoice.LAST_30_DAYS:
            start_date = now - dt.timedelta(days=30)
        case TimeRangeChoice.LAST_7_DAYS:
            start_date = now - dt.timedelta(days=7)
        case TimeRangeChoice.CUSTOM:
            start_date = None
            end_date = None
        case TimeRangeChoice.LAST_WEEK:
            start_date = now - dt.timedelta(days=weekday_int + 7)
            end_date = start_date + dt.timedelta(days=6)
        case TimeRangeChoice.LAST_MONTH:
            end_date = now - dt.timedelta(days=now.day)
            start_date = end_date.replace(day=1)
        case _:
            start_date = None
            end_date = None

    if force_date:
        start_date = start_date.date() if start_date else None
        end_date = end_date.date() if end_date else None

    return start_date, end_date
