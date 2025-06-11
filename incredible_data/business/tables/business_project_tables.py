from typing import final

import django_tables2 as tables
from django.db import models
from django.utils.translation import gettext_lazy as _

from incredible_data.business.models.business_accounting_models import Order
from incredible_data.business.models.business_project_models import Project


@final
class ProjectTable(tables.Table):
    number = tables.Column(_("Number"), linkify=True)

    class Meta:
        model: type[models.Model] = Project
        fields: list[str] = ["number", "name", "order__customer"]


@final
class OrderTable(tables.Table):
    number = tables.Column(_("Order"), linkify=True)

    class Meta:
        model: type[models.Model] = Order
        fields: list[str] = ["number", "customer", "expected_date"]
