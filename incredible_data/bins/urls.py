# ruff: noqa: E501
from django.urls import path

from .bins_views import ContainerCreateView, ContainerDetailView, ContainerListView

app_name = "bins"
# fmt: off
urlpatterns = [
    path("", ContainerListView.as_view(), name="container_list"),
    path("new/", ContainerCreateView.as_view(), name="container_add"),
    path("<slug:slug>/", ContainerDetailView.as_view(), name="container_detail"),
]

# fmt: on
