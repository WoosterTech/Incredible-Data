import logging
from typing import final

from django_filters import rest_framework as filters

from incredible_data.mood.models import Entry, Metric, MetricType

logger = logging.getLogger(__name__)


@final
class MetricTypeFilter(filters.FilterSet):
    min_value = filters.NumericRangeFilter()
    max_value = filters.NumericRangeFilter()

    @final
    class Meta:
        model = MetricType
        fields = {
            "name": ["iexact", "icontains"],
            "is_score": ["exact"],
            "higher_is_better": ["exact"],
        }


@final
class MetricFilter(filters.FilterSet):
    date = filters.DateFromToRangeFilter(field_name="entry__created_on")
    o = filters.OrderingFilter(fields=(("metric_type__name", "metric_type"),))

    @final
    class Meta:
        model = Metric
        fields = ["entry", "metric_type"]


@final
class EntryFilter(filters.FilterSet):
    date = filters.DateFromToRangeFilter(field_name="created_on")
    o = filters.OrderingFilter(
        fields=(("time_of_day", "time_of_day"), ("created_on", "created_on"))
    )

    @final
    class Meta:
        model = Entry
        fields = ["time_of_day"]
