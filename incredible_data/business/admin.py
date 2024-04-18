from django.contrib import admin

from incredible_data.contacts.admin import UserStampedModelAdmin

from .models.business_accounting_models import Invoice, InvoiceLine, Order
from .models.business_project_models import Project


# Register your models here.
class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    readonly_fields = ["rank", "extended_price"]
    fields = ["rank", "description", "quantity", "unit_price", "extended_price"]


@admin.register(Order)
class OrderAdmin(UserStampedModelAdmin):
    list_display = ["number", "customer", "expected_date"]
    list_filter = ["customer"]
    date_hierarchy = "created"
    search_fields = ["number", "customer"]


@admin.register(Invoice)
class InvoiceAdmin(UserStampedModelAdmin):
    list_display = ["number", "customer", "status"]
    list_filter = ["customer"]
    date_hierarchy = "created"
    search_fields = ["number", "customer"]
    readonly_fields = ["status_changed"]
    inlines = [InvoiceLineInline]


@admin.register(Project)
class ProjectAdmin(UserStampedModelAdmin):
    list_display = ["number", "customer", "name"]
    list_filter = ["customer"]
    date_hierarchy = "created"
    search_fields = ["project_number", "customer", "name"]
