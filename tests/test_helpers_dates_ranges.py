# pyright: reportUnusedParameter=false

import datetime as dt
from typing import Any
from unittest import mock

import pytest
from django.utils import timezone

from incredible_data.helpers.dates.ranges import (
    TimeRangeChoice,
    get_dates,
    get_weekday_int,
)

MONDAY_WITH_SUNDAY_INDEX = 1
MONDAY_WITH_MONDAY_INDEX = 0


class TestGetWeekdayInt:
    @pytest.fixture
    def mock_now(self):
        """Mock timezone.now() to return a fixed datetime for consistent testing."""
        # Fixed datetime: Monday, September 22, 2025, 10:30:00 UTC
        fixed_datetime = timezone.datetime(2025, 9, 22, 10, 30, 0, tzinfo=dt.UTC)
        with mock.patch(
            "incredible_data.helpers.dates.ranges.timezone.now"
        ) as mock_tz_now:
            mock_tz_now.return_value = fixed_datetime
            yield fixed_datetime

    def test_get_weekday_int(self, mock_now: dt.datetime):
        assert get_weekday_int(mock_now) == MONDAY_WITH_SUNDAY_INDEX

    def test_get_weekday_int_monday(self, mock_now: dt.datetime):
        """Test get_weekday_int for Monday."""
        assert (
            get_weekday_int(mock_now, week_starts_on="monday")
            == MONDAY_WITH_MONDAY_INDEX
        )


class TestGetDates:
    """Test cases for the get_dates function."""

    @pytest.fixture
    def mock_now(self):
        """Mock timezone.now() to return a fixed datetime for consistent testing."""
        # Fixed datetime: Wednesday, September 22, 2025, 10:30:00 UTC
        fixed_datetime = timezone.datetime(2025, 9, 22, 10, 30, 0, tzinfo=dt.UTC)
        with mock.patch(
            "incredible_data.helpers.dates.ranges.timezone.now"
        ) as mock_tz_now:
            mock_tz_now.return_value = fixed_datetime
            yield fixed_datetime

    def test_get_dates_none_period(self, mock_now: dt.datetime):
        """Test get_dates with None period returns (None, None)."""
        start_date, end_date = get_dates(None)
        assert start_date is None
        assert end_date is None

    def test_get_dates_none_period_force_date(self, mock_now: dt.datetime):
        """Test get_dates with None period and force_date=True returns (None, None)."""
        start_date, end_date = get_dates(None, force_date=True)
        assert start_date is None
        assert end_date is None

    def test_get_dates_today(self, mock_now: dt.datetime):
        """Test get_dates with TODAY period."""
        start_date, end_date = get_dates(TimeRangeChoice.TODAY)

        assert start_date == mock_now
        assert end_date == mock_now

    def test_get_dates_today_force_date(self, mock_now: dt.datetime):
        """Test get_dates with TODAY period and force_date=True."""
        start_date, end_date = get_dates(TimeRangeChoice.TODAY, force_date=True)

        expected_date = mock_now.date()
        assert start_date == expected_date
        assert end_date == expected_date
        assert isinstance(start_date, dt.date)
        assert isinstance(end_date, dt.date)

    def test_get_dates_this_week(self, mock_now: dt.datetime):
        """Test get_dates with THIS_WEEK period.

        For Monday Sep 22, 2025 (weekday 1), this_week should start on Sunday Sep 21.
        """
        start_date, end_date = get_dates(TimeRangeChoice.THIS_WEEK)

        # Monday has weekday_int=1 (using Sunday=0 convention), so start should be 1 days back
        expected_start = mock_now - dt.timedelta(days=MONDAY_WITH_SUNDAY_INDEX)
        assert start_date == expected_start
        assert end_date == mock_now

    def test_get_dates_this_month(self, mock_now: dt.datetime):
        """Test get_dates with THIS_MONTH period."""
        start_date, end_date = get_dates(TimeRangeChoice.THIS_MONTH)

        expected_start = mock_now.replace(day=1)
        assert start_date == expected_start
        assert end_date == mock_now

    def test_get_dates_last_30_days(self, mock_now: dt.datetime):
        """Test get_dates with LAST_30_DAYS period."""
        start_date, end_date = get_dates(TimeRangeChoice.LAST_30_DAYS)

        expected_start = mock_now - dt.timedelta(days=30)
        assert start_date == expected_start
        assert end_date == mock_now

    def test_get_dates_last_7_days(self, mock_now: dt.datetime):
        """Test get_dates with LAST_7_DAYS period."""
        start_date, end_date = get_dates(TimeRangeChoice.LAST_7_DAYS)

        expected_start = mock_now - dt.timedelta(days=7)
        assert start_date == expected_start
        assert end_date == mock_now

    def test_get_dates_last_week(self, mock_now: dt.datetime):
        """Test get_dates with LAST_WEEK period.

        For Monday Sep 22, 2025, last week should be Sun Sep 14 - Sat Sep 20.
        """
        start_date, end_date = get_dates(TimeRangeChoice.LAST_WEEK)

        # weekday_int=3, so last week starts 3+7=10 days back
        expected_start = mock_now - dt.timedelta(days=8)  # Sep 14
        expected_end = expected_start + dt.timedelta(days=6)  # Sep 20

        assert start_date == expected_start
        assert end_date == expected_end

    def test_get_dates_last_month(self, mock_now: dt.datetime):
        """Test get_dates with LAST_MONTH period."""
        start_date, end_date = get_dates(TimeRangeChoice.LAST_MONTH)

        # End of last month (Aug 31, 2025)
        expected_end = mock_now - dt.timedelta(
            days=mock_now.day
        )  # Sep 22 - 22 days = Aug 31
        # Start of last month (Aug 1, 2025)
        expected_start = expected_end.replace(day=1)

        assert start_date == expected_start
        assert end_date == expected_end

    def test_get_dates_custom(self, mock_now: dt.datetime):
        """Test get_dates with CUSTOM period returns (None, None)."""
        start_date, end_date = get_dates(TimeRangeChoice.CUSTOM)

        assert start_date is None
        assert end_date is None

    def test_get_dates_custom_force_date(self, mock_now: dt.datetime):
        """Test get_dates with CUSTOM period and force_date=True returns (None, None)."""
        start_date, end_date = get_dates(TimeRangeChoice.CUSTOM, force_date=True)

        assert start_date is None
        assert end_date is None

    def test_get_dates_force_date_conversion(self, mock_now: dt.datetime):
        """Test that force_date=True converts datetime to date objects."""
        start_date, end_date = get_dates(TimeRangeChoice.LAST_7_DAYS, force_date=True)

        assert isinstance(start_date, dt.date)
        assert isinstance(end_date, dt.date)
        assert not isinstance(start_date, dt.datetime)
        assert not isinstance(end_date, dt.datetime)

        expected_start = (mock_now - dt.timedelta(days=7)).date()
        expected_end = mock_now.date()

        assert start_date == expected_start
        assert end_date == expected_end

    @pytest.mark.parametrize(
        "invalid_period",
        [
            "invalid_string",
            123,
            [],
            {},
        ],
    )
    def test_get_dates_invalid_period(
        self,
        mock_now: dt.datetime,
        invalid_period: str | int | list[Any] | dict[Any, Any],  # pyright: ignore[reportExplicitAny]
    ):
        """Test get_dates with invalid period values returns (None, None)."""
        start_date, end_date = get_dates(invalid_period)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType]

        assert start_date is None
        assert end_date is None

    @pytest.mark.parametrize(
        ("now_mock", "expected_start", "expected_end"),
        [
            (
                timezone.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.UTC),
                timezone.datetime(2024, 1, 1, 0, 0, 0, tzinfo=dt.UTC),
                timezone.datetime(2024, 1, 1, 23, 59, 59, tzinfo=dt.UTC),
            ),
            (
                timezone.datetime(2024, 6, 15, 18, 30, 0, tzinfo=dt.UTC),
                timezone.datetime(2024, 6, 15, 0, 0, 0, tzinfo=dt.UTC),
                timezone.datetime(2024, 6, 15, 23, 59, 59, tzinfo=dt.UTC),
            ),
            (
                timezone.datetime(2023, 12, 31, 23, 59, 59, tzinfo=dt.UTC),
                timezone.datetime(2023, 12, 31, 0, 0, 0, tzinfo=dt.UTC),
                timezone.datetime(2023, 12, 31, 23, 59, 59, tzinfo=dt.UTC),
            ),
        ],
    )
    def test_get_dates_with_different_mock_dates(
        self,
        now_mock: dt.datetime,
        expected_start: dt.datetime,
        expected_end: dt.datetime,
    ):
        """Test get_dates behavior with different mock dates to ensure consistency."""

        with mock.patch(
            "incredible_data.helpers.dates.ranges.timezone.now"
        ) as mock_tz_now:
            mock_tz_now.return_value = now_mock

            # Test TODAY
            start, end = get_dates(TimeRangeChoice.TODAY)
            assert start == now_mock
            assert end == now_mock

            # Test LAST_7_DAYS
            start, end = get_dates(TimeRangeChoice.LAST_7_DAYS)
            assert start == now_mock - dt.timedelta(days=7)
            assert end == now_mock

            # Test THIS_MONTH
            start, end = get_dates(TimeRangeChoice.THIS_MONTH)
            assert start == now_mock.replace(day=1)
            assert end == now_mock

    def test_get_dates_edge_case_month_boundary(self):
        """Test get_dates behavior at month boundaries."""
        # Test at the beginning of a month
        first_of_month = timezone.datetime(2024, 3, 1, 10, 0, 0, tzinfo=dt.UTC)

        with mock.patch(
            "incredible_data.helpers.dates.ranges.timezone.now"
        ) as mock_tz_now:
            mock_tz_now.return_value = first_of_month

            # THIS_MONTH should start on the same day
            start, end = get_dates(TimeRangeChoice.THIS_MONTH)
            assert start == first_of_month.replace(day=1)
            assert end == first_of_month

            # LAST_MONTH should be February
            start, end = get_dates(TimeRangeChoice.LAST_MONTH)
            # End of last month (Feb 29, 2024 - leap year)
            expected_end = first_of_month - dt.timedelta(days=1)  # Feb 29
            expected_start = expected_end.replace(day=1)  # Feb 1

            assert start == expected_start
            assert end == expected_end
