from typing import final

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from incredible_data.customers.models import Customer


@final
class CustomerTable(tables.Table):
    name = tables.Column(_("Customer"), linkify=True)

    @final
    class Meta:
        model = Customer
        fields = ["name", "main_phone"]
