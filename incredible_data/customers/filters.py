from typing import final

import django_filters as filters

from incredible_data.customers.models import Customer


@final
class CustomerFilter(filters.FilterSet):  # pyright: ignore[reportUnknownMemberType, reportUntypedBaseClass, reportAttributeAccessIssue]
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    @final
    class Meta:
        model = Customer
        fields = ("name",)
