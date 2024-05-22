from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from incredible_data.bins.bins_forms import NewContainerForm
from incredible_data.bins.bins_tables import ContainerTable
from incredible_data.bins.models.bins_container_models import Container
from incredible_data.helpers.helper_views import (
    ExtraContextDetailView,
    SingleTableListView,
)


class ContainerListView(PermissionRequiredMixin, SingleTableListView):
    model = Container
    template_name = "bins/container_list.html"
    actions = [(_("New Container"), reverse_lazy("bins:container_add"))]
    table_class = ContainerTable
    permission_required = "bins.view_container"


class ContainerDetailView(PermissionRequiredMixin, ExtraContextDetailView):
    model = Container
    template_name = "bins/container_detail.html"
    permission_required = "bins.view_container"


class ContainerCreateView(PermissionRequiredMixin, CreateView):
    model = Container
    template_name = "bins/container_form.html"
    permission_required = "bins.add_container"
    form_class = NewContainerForm
    success_url = reverse_lazy("bins:container_list")
