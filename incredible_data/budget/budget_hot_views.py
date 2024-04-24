from django.forms import DateInput  # noqa: F401
from django.urls import reverse_lazy  # noqa: F401
from funky_sheets.formsets import HotView

from .models import ReceiptItem


class CreateReceiptItemView(HotView):
    model = ReceiptItem
    template_name = "budget/create.html"
    prefix = "table"
    fields = (
        "product_code",
        "description",
        "total_price",
    )
    hot_settings = {
        "licenseKey": "non-commercial-and-evaluation",
    }


class UpdateReceiptItemsView(HotView):
    model = ReceiptItem
    template_name = "budget/items_update.html"
