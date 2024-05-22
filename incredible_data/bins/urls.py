# ruff: noqa: E501
from django.urls import path

from .bins_views import (
    ContainerAttachmentCreateView,
    ContainerAttachmentDeleteView,
    ContainerCreateView,
    ContainerDeleteView,
    ContainerDetailView,
    ContainerListView,
)

app_name = "bins"
# fmt: off
urlpatterns = [
    path("", ContainerListView.as_view(), name="container_list"),
    path("new/", ContainerCreateView.as_view(), name="container_add"),
    path("<slug:slug>/", ContainerDetailView.as_view(), name="container_detail"),
    path("<slug:slug>/delete/", ContainerDeleteView.as_view(), name="container_delete"),
    path("attachment/new/", ContainerAttachmentCreateView.as_view(), name="container_attachment_add"),
    path("attachment/<int:pk>/delete/", ContainerAttachmentDeleteView.as_view(), name="container_attachment_delete"),
]

# fmt: on
