import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from incredible_data.business.models.business_accounting_models import Invoice


class InvoiceTable(tables.Table):
    number = tables.Column(_("number"), linkify=True)

    class Meta:
        model = Invoice
        fields = ["number", "status", "customer", "grand_total", "order"]
