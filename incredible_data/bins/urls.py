# ruff: noqa: E501
from django.urls import path

from .views import ContainerDetailView, ContainerListView

app_name = "bins"
# fmt: off
urlpatterns = [
    path("<slug:slug>/", ContainerDetailView.as_view(), name="container_detail"),
    path("", ContainerListView.as_view(), name="container_list"),
]

# fmt: on
