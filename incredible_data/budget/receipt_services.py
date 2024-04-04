from decimal import Decimal
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from celery import shared_task
from django.conf import settings
from pydantic import BaseModel

from .models.budget_receipt_models import Receipt

AZURE_ENDPOINT = settings.AZURE_ENDPOINT
AZURE_KEY = settings.AZURE_KEY
LOCALE = settings.LANGUAGE_CODE
ML_MODEL = "prebuilt-receipt"


class BasicReceipt(BaseModel):
    merchant_name: str
    merchant_name_confidence: Decimal
    transaction_date: str
    transaction_date_confidence: Decimal


def populate_receipt_model(receipt_model_id: int) -> None:
    receipt_model = Receipt.objects.get(id=receipt_model_id)
    analyzed_receipt_result = analyze_receipt_file(receipt_model.receipt_file.path)

    receipt_dict = {}
    for _idx, receipt in enumerate(analyzed_receipt_result.documents):
        merchant_object = receipt.fields.get("MerchantName")
        receipt_dict["merchant_name",] = merchant_object.value_string


@shared_task
def analyze_receipt_file(filepath: str | Path):
    receipt_file = Path(filepath)

    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY)
    )

    with Path.open(receipt_file, "rb") as f:
        poller = client.begin_analyze_document(
            ML_MODEL, analyze_request=f, locale=LOCALE
        )

    return poller.result()
