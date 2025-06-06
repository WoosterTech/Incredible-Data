from typing import Any, cast, final, override

from django.http import HttpRequest
from django.shortcuts import render
from django.urls import path, reverse  # pyright: ignore[reportUnknownVariableType]
from neapolitan.views import Role

from incredible_data.business.tables.business_accounting_tables import InvoiceTable
from incredible_data.business.tables.business_project_tables import (
    OrderTable,
    ProjectTable,
)
from incredible_data.helpers.helper_views import CustomCRUDView, SingleTableListView

from .models.business_accounting_models import Invoice, Order
from .models.business_project_models import Project


# Create your views here.
def printable_invoice(request: HttpRequest, slug: str):
    invoice = (
        Invoice.objects.filter(slug=slug)
        .select_related("customer")
        .prefetch_related("invoiceline_set")
    )
    context = {"invoice": invoice.first()}
    return render(request, "business/invoice.html", context)


@final
class ProjectListView(SingleTableListView):
    view_title = "Projects"
    model = Project
    table_class = ProjectTable
    template_name = "base_list_tables2.html"


@final
class ProjectView(CustomCRUDView):
    model = Project
    fields = ["number", "name", "customer", "notes", "order"]
    lookup_field = "slug"
    path_converter = "slug"
    list_view = ProjectListView


@final
class OrderListView(SingleTableListView):
    view_title = "Orders"
    model = Order
    table_class = OrderTable
    template_name = "base_list_tables2.html"


@final
class OrderView(CustomCRUDView):
    model = Order
    fields = ["customer", "expected_date", "notes"]
    list_view = OrderListView


@final
class InvoiceListView(SingleTableListView):
    view_title = "Invoices"
    model = Invoice
    table_class = InvoiceTable
    template_name = "base_list_tables2.html"


@final
class InvoiceView(CustomCRUDView):
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
    lookup_field: str = "slug"
    path_converter: str = "slug"
    list_view = InvoiceListView

    @override
    @classmethod
    def additional_urls(cls):
        urls = super().additional_urls()
        detail_url = Role.DETAIL.url_pattern(cls)
        printable_url = path(
            detail_url + "printable/", printable_invoice, name="invoice_printable"
        )

        urls.append(printable_url)
        return urls

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, object]:  # pyright: ignore[reportAny, reportExplicitAny]
        context = cast("dict[str, object]", super().get_context_data(**kwargs))  # pyright: ignore[reportAny, reportUnknownMemberType]

        lookup_value = getattr(self.object, self.lookup_field)  # pyright: ignore[reportAny]
        printable_action = {
            "label": "Printable Invoice",
            "href": reverse(
                "invoice_printable", kwargs={self.lookup_field: lookup_value}
            ),
        }
        action_links = cast("list[dict[str,str]]", context.get("action_links", []))
        if self.role == Role.DETAIL:
            action_links.append(printable_action)
        context["action_links"] = action_links

        return context
