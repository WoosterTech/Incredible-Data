from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from incredible_data.bins.bins_tables import ContainerTable
from incredible_data.bins.models.bins_container_models import Container
from incredible_data.helpers.helper_views import (
    ExtraContextDetailView,
    SingleTableListView,
)


class ContainerListView(SingleTableListView):
    model = Container
    template_name = "bins/container_list.html"
    actions = [(_("New Container"), reverse_lazy("admin:bins_container_add"))]
    table_class = ContainerTable


class ContainerDetailView(ExtraContextDetailView):
    model = Container
    template_name = "bins/container_detail.html"
