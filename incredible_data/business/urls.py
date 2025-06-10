# ruff: noqa: E501
from django.urls import path
from neapolitan.views import Role

from .views import (
    InvoiceView,
    OrderView,
    ProjectView,
    invoice_create_view,
    printable_invoice,
    project_create_view,
    project_detail_view,
    project_edit_view,
    project_list_view,
)

app_name = "business"
# fmt: off
urlpatterns = [
    path("invoices/<str:slug>/printable", printable_invoice, name="invoice_detail_printable"),
    path("project/new/", project_create_view, name="project-create"),
    path("project/<slug:slug>/edit/", project_edit_view, name="project-update"),
    path("project/<slug:slug>/", project_detail_view, name="project-detail"),
    path("project/", project_list_view, name="project-list"),
    *ProjectView.get_urls(roles=[Role.DELETE]),
    *OrderView.get_urls(roles=[Role.DELETE, Role.DETAIL, Role.LIST, Role.UPDATE]),
    path("invoice/new/", invoice_create_view, name="invoice-create"),
    *InvoiceView.get_urls(roles=[Role.DETAIL, Role.DELETE, Role.LIST]),
]
