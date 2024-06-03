import logging

from django.conf import settings
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import ExpenseCategory, Merchant, Receipt, ReceiptFile, ReceiptItem
from .receipt_services import analyze_receipt_file, create_receipt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)


@admin.register(ReceiptFile)
class ReceiptFileAdmin(admin.ModelAdmin):
    readonly_fields = ["analyzed_datetime", "analyze_result"]
    list_display = ["file_name", "file", "analyzed_datetime"]
    actions = ["analyze_receipt_file", "create_receipt_objects"]

    @admin.action(description="Analyze selected receipts")
    def analyze_receipt_file(
        self, request: HttpRequest, queryset: QuerySet[ReceiptFile]
    ):
        for file in queryset:
            self.message_user(
                request, f"Sending {file.file} for analysis...", messages.INFO
            )
            msg = f"File pk: {file.pk}"
            logger.debug(msg)
            analyze_receipt_file.delay(file.pk)

    @admin.display(description="File name")
    def file_name(self, obj):
        return obj.file.name

    @admin.display(description="Create receipts from files")
    def create_receipt_objects(
        self, request: HttpRequest, queryset: QuerySet[ReceiptFile]
    ):
        for file in queryset:
            try:
                receipt, created = create_receipt(file)
            except ValueError:
                msg = f"Receipt {file} must be analyzed before creating receipt model."
                self.message_user(request, msg, messages.WARNING)
            except settings.ImproperlyConfigured:
                msg = "Azure settings are not set."
                self.message_user(request, msg, messages.ERROR)
            else:
                msg = f"'{receipt}' created." if created else f"'{receipt}' updated."
                self.message_user(request, msg, messages.SUCCESS)


admin.site.register(Merchant)


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    inlines = [ReceiptItemInline]


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ["product_code", "expense_category", "description", "total_price"]
    list_filter = ["parent_receipt", "expense_category"]
    list_editable = ["expense_category"]


admin.site.register(ExpenseCategory)
