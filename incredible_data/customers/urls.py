from django.urls import path

from incredible_data.customers.views import (
    customer_create_view,
    customer_detail_view,
    customer_edit_view,
    customer_list_view,
)

app_name = "customers"
# fmt: off
urlpatterns = [
    path("create/", customer_create_view, name="customer-create"),
    path("<slug:slug>/edit/", customer_edit_view, name="customer-update"),
    path("<slug:slug>/", customer_detail_view, name="customer-detail"),
    path("", customer_list_view, name="customer-list"),
]
# fmt: on
