from django.urls import path

from .budget_hot_views import CreateReceiptItemView

app_name = "budget"
urlpatterns = [
    path("create/", CreateReceiptItemView.as_view(), name="create_receiptitem"),
]
