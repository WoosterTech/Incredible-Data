import json
import logging
from datetime import datetime as dt
from pathlib import Path

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import get_current_timezone
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime

from incredible_data.budget.models import ReceiptItem
from incredible_data.budget.receipt_services import create_receipt

APPS_DIR = settings.APPS_DIR

logger = logging.getLogger(__name__)


def get_example_json() -> str:
    json_file_path = Path(
        APPS_DIR, "budget", "fixtures", "budget", "example_receipt_result.json"
    )
    with Path.open(json_file_path, "rb") as f:
        analysis_dict: dict = json.load(f)

    analyze_result_dict = analysis_dict.get("analyzeResult")

    return json.dumps(analyze_result_dict)


class ReceiptFileFactory(DjangoModelFactory):
    class Meta:
        model = "budget.ReceiptFile"

    file = SimpleUploadedFile(
        "test_receipt.pdf", b"test file content", content_type="application/pdf"
    )
    analyze_result = get_example_json()
    analyzed_datetime = FuzzyDateTime(
        dt(2024, 1, 1, 1, 24, tzinfo=get_current_timezone())
    )


@pytest.mark.django_db()
class TestReceipts:
    def test_receipt_object_creation(self):
        receipt_file = ReceiptFileFactory()

        receipt_obj, created = create_receipt(receipt_file)

        receiptitem_qs = ReceiptItem.objects.filter(
            parent_receipt=receipt_obj
        ).order_by("total_price")

        receipt_item_count = 3
        cheapest_item_description = "Beer"
        assert len(receiptitem_qs) == receipt_item_count
        assert receiptitem_qs.first().description == cheapest_item_description
