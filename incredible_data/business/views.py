from django.shortcuts import render
from django_tables2 import SingleTableView
from neapolitan.views import CRUDView

from incredible_data.business.tables.business_accounting_tables import InvoiceTable
from incredible_data.business.tables.business_project_tables import ProjectTable

from .models.business_accounting_models import Invoice, Order
from .models.business_project_models import Project


# Create your views here.
def printable_invoice(request, slug: str):
    invoice = (
        Invoice.objects.filter(slug=slug)
        .select_related("customer")
        .prefetch_related("invoiceline_set")
    )
    context = {"invoice": invoice.first()}
    return render(request, "business/invoice.html", context)


class ProjectView(CRUDView):
    model = Project
    fields = ["number", "name", "customer", "notes", "order"]
    lookup_field = "slug"


class ProjectListView(SingleTableView):
    model = Project
    table_class = ProjectTable
    template_name = "base_list_tables2.html"


class OrderView(CRUDView):
    model = Order
    fields = ["customer", "expected_date", "notes"]


class InvoiceView(CRUDView):
    model = Invoice
    fields = [
        "number",
        "status",
        "customer",
        "terms",
        "notes",
        "grand_total",
        "due_date",
        "order",
    ]
    lookup_field = "slug"
    path_converter = "slug"


class InvoiceListView(SingleTableView):
    model = Invoice
    table_class = InvoiceTable
    template_name = "base_list_tables2.html"
