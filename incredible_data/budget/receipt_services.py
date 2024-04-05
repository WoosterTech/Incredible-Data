from decimal import Decimal
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from celery import shared_task
from django.conf import settings

from .models.budget_receipt_models import Merchant, Receipt

AZURE_ENDPOINT = settings.AZURE_ENDPOINT
AZURE_KEY = settings.AZURE_KEY
LOCALE = settings.LANGUAGE_CODE
ML_MODEL = "prebuilt-receipt"


def populate_receipt_model(receipt_model_id: int) -> None:
    receipt_model = Receipt.objects.get(id=receipt_model_id)
    analyzed_receipt_result = analyze_receipt_file(receipt_model.receipt_file.path)

    for _idx, receipt in enumerate(analyzed_receipt_result.documents):
        merchant_object = receipt.fields.get("MerchantName")
        merchant_name = merchant_object.value_string
        merchant_name_confidence = merchant_object.confidence
        transaction_object = receipt.fields.get("TransactionDate")
        transaction_date = transaction_object.value_date
        transaction_date_confidence = transaction_object.confidence

        merchant_object, _ = Merchant.objects.get_or_create(
            title=merchant_name, defaults={"verified": False}
        )

        receipt_model.merchant = merchant_object
        receipt_model.merchant_confidence = Decimal(merchant_name_confidence)
        receipt_model.transaction_date = transaction_date
        receipt_model.transaction_date_confidence = Decimal(transaction_date_confidence)

        receipt_model.save()


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
