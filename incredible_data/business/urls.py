# ruff: noqa: E501
from django.urls import path
from neapolitan.views import Role

from .views import (
    InvoiceView,
    OrderView,
    ProjectView,
    invoice_create_view,
    invoice_detail_view,
    order_detail_view,
    printable_invoice,
    project_create_view,
    project_detail_view,
    project_edit_view,
)

app_name = "business"
# fmt: off
urlpatterns = [
    path("invoice/<str:slug>/printable", printable_invoice, name="invoice_detail_printable"),
    path("project/new/", project_create_view, name="project-create"),
    path("project/<slug:slug>/edit/", project_edit_view, name="project-update"),
    path("project/<slug:slug>/", project_detail_view, name="project-detail"),
    *ProjectView.get_urls(roles=[Role.DELETE, Role.LIST]),
    path("order/<slug:slug>/", order_detail_view, name="order-detail"),
    *OrderView.get_urls(roles=[Role.DELETE, Role.LIST, Role.UPDATE]),
    path("invoice/new/", invoice_create_view, name="invoice-create"),
    path("invoice/<slug:slug>/", invoice_detail_view, name="invoice-detail"),
    *InvoiceView.get_urls(roles=[Role.DELETE, Role.LIST]),
]
