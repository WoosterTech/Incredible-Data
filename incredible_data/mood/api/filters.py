from typing import final

from django_filters import rest_framework as filters

from incredible_data.mood.models import MetricType


@final
class MetricTypeFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    min_value = filters.NumberFilter(lookup_expr="eq")
    max_value = filters.NumberFilter(lookup_expr="eq")
    min_value__gte = filters.NumberFilter(field_name="min_value", lookup_expr="gte")
    min_value__lte = filters.NumberFilter(field_name="min_value", lookup_expr="lte")
    max_value__gte = filters.NumberFilter(field_name="max_value", lookup_expr="gte")
    max_value__lte = filters.NumberFilter(field_name="max_value", lookup_expr="lte")

    @final
    class Meta:
        model = MetricType
        fields = ["is_score", "higher_is_better"]
