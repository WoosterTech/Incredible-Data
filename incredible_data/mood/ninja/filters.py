import datetime as dt
import logging
from enum import StrEnum
from functools import wraps
from typing import Any

from django.db.models import Q
from ninja import FilterSchema
from pydantic import Field, model_validator

from incredible_data.mood.models import Entry

logger = logging.getLogger(__name__)


def today() -> dt.date:
    now = dt.datetime.now(tz=dt.UTC)
    return now.date()


@wraps(dt.timedelta)
def tdelta(hours: int) -> dt.timedelta:
    return dt.timedelta(hours=hours)


def days_this_week() -> int:
    today = dt.datetime.now(tz=dt.UTC).date()
    start_of_week = today - dt.timedelta(days=today.weekday())
    return (today - start_of_week).days + 1


def this_week_start() -> int:
    return today() - dt.timedelta(days=days_this_week())


def this_month_start() -> dt.date:
    today = dt.datetime.now(tz=dt.UTC).date()
    return today.replace(day=1)


def last_week_start() -> dt.date:
    start_of_week = this_week_start()
    return start_of_week - dt.timedelta(days=7)


def last_month_start() -> dt.date:
    first_day_of_current_month = this_month_start()
    return (first_day_of_current_month - dt.timedelta(days=1)).replace(day=1)


PERIOD_MAPPING = {
    "last_30_days": Q(effective_date__gte=today() - tdelta(720)),
    "this_week": Q(effective_date__gte=this_week_start()),
    "this_month": Q(effective_date__gte=this_month_start()),
    "last_week": Q(effective_date__range=(last_week_start(), this_week_start())),
    "last_month": Q(effective_date__range=(last_month_start(), this_month_start())),
    "last_7_days": Q(effective_date__gte=today() - tdelta(168)),
    "today": Q(effective_date=today()),
}


class Period(StrEnum):
    TODAY = "today"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    CUSTOM = "custom"

    def expression(self) -> Q:
        """Convert the period to a Django Q object for filtering."""
        return PERIOD_MAPPING.get(self, Q())


class EntryFilters(FilterSchema):
    period: Period | None = Period.LAST_30_DAYS
    start: dt.date | None = Field(None, q="effective_date__gte")
    end: dt.date | None = Field(None, q="effective_date__lte")
    search: str | None = Field(None, q=["notes__icontains"])
    time_of_day: Entry.TimeOfDay | None = None

    def filter_period(self, value: Period | None) -> Q:
        if value is None:
            return Q()

        if value is Period.CUSTOM:
            return Q()

        query_expression = value.expression()

        logger.debug("Period filter Q: %s", query_expression)

        return query_expression

    @model_validator(mode="before")
    @classmethod
    def validate_custom_period(cls, data: Any) -> Any:
        period = getattr(data, "period", None)
        start = getattr(data, "start", None)
        end = getattr(data, "end", None)
        if period == Period.CUSTOM and (start is None and end is None):
            msg = "Custom period requires at least one of start or end date."
            raise ValueError(msg)

        return data


class TrendFilters(FilterSchema):
    id__in: list[int] | None = None
