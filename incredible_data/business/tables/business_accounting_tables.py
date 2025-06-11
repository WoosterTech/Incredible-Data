from typing import final

import django_tables2 as tables
from django.db import models
from django.utils.translation import gettext_lazy as _

from incredible_data.business.models.business_accounting_models import Invoice


@final
class InvoiceTable(tables.Table):
    number = tables.Column(_("Number"), linkify=True)
    order__number = tables.Column(_("Order"))

    class Meta:
        model: type[models.Model] = Invoice
        fields: list[str] = [
            "number",
            "status",
            "customer",
            "grand_total",
            "order__number",
        ]
