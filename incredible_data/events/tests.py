import datetime as dt

import pytest

from incredible_data.events.models import event_age

TEN_YEARS = 10


# Create your tests here.
@pytest.fixture
def past_datetime():
    return dt.datetime(2021, 1, 1, 0, 0, 0, tzinfo=dt.UTC)


@pytest.fixture
def ten_years_later(past_datetime: dt.datetime):
    return past_datetime.replace(year=past_datetime.year + TEN_YEARS)


def test_age_function(past_datetime: dt.datetime, ten_years_later: dt.datetime):
    assert (
        event_age(current_date=ten_years_later, start_date=past_datetime) == TEN_YEARS
    )
