import json
import logging
from decimal import Decimal
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# HttpResponseError is pulled into admin
from azure.core.exceptions import HttpResponseError  # noqa: F401
from benedict import benedict
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Merchant, Receipt, ReceiptFile, ReceiptItem

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

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


def create_receipt(receipt_file: ReceiptFile) -> str:
    if receipt_file.analyze_result is None:
        msg = "must analyze receipt file before creating receipt object"
        raise ValueError(msg)
    analyze_json = json.loads(receipt_file.analyze_result)
    analysis_b = benedict(analyze_json)
    fields = benedict()
    for document in analysis_b.documents:
        fields.merge(document.fields)

    merchant = fields.MerchantName

    merchant_object, _ = Merchant.objects.get_or_create(
        title=merchant.valueString, defaults={"verified": False}
    )

    transaction = fields.TransactionDate
    total = fields.Total

    receipt_obj, created = Receipt.objects.update_or_create(
        receipt_file=receipt_file,
        defaults={
            "merchant": merchant_object,
            "merchant_confidence": merchant.confidence,
            "transaction_date": transaction.valueDate,
            "transaction_date_confidence": transaction.confidence,
            "grand_total": total.valueCurrency.amount,
            "grand_total_confidence": total.confidence,
        },
    )

    items: list[benedict] = fields.Items.valueArray

    if not created:
        count, _ = ReceiptItem.objects.filter(parent_receipt=receipt_obj).delete()
        msg = f"{count} receipt items deleted."
        logger.info(msg)

    for item in items:
        item_obj = item.valueObject

        try:
            item_description = item_obj.Description.valueString
        except AttributeError:
            item_description = ""
        try:
            item_product_code = item_obj.ProductCode.valueString
        except AttributeError:
            item_product_code = item_description

        try:
            item_total_price = item_obj.TotalPrice.valueCurrency.amount
            this_receipt = Receipt.objects.get(pk=receipt_obj.pk)
        except AttributeError:
            msg = f"item {item.valueObject} is not fully valid"
            logger.debug(msg)
        else:
            _ = ReceiptItem.objects.create(
                parent_receipt=this_receipt,
                product_code=item_product_code,
                description=item_description,
                total_price=item_total_price,
            )
    return receipt_obj, created


@shared_task()
def analyze_receipt_file(file_pk) -> None:
    file_object = ReceiptFile.objects.get(pk=file_pk)
    msg = f"file_object name: {file_object.file.name}"
    logger.debug(msg)
    receipt_file_path = Path(file_object.file.path)

    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY)
    )

    with Path.open(receipt_file_path, "rb") as f:
        result = client.begin_analyze_document(
            ML_MODEL,
            analyze_request=f,
            locale=LOCALE,
            content_type="application/octet-stream",
        )

    result_dict = result.result().as_dict()
    result_json = json.dumps(result_dict)

    file_object.analyze_result = result_json
    file_object.analyzed_datetime = timezone.now()

    file_object.save()
