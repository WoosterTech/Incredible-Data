from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import DeleteView

from incredible_data.bins.bins_forms import ContainerAttachmentForm, NewContainerForm
from incredible_data.bins.bins_tables import ContainerTable
from incredible_data.bins.models.bins_container_models import (
    Container,
    ContainerAttachment,
)
from incredible_data.helpers.helper_views import (
    ExtraContextDetailView,
    SingleTableListView,
    UserStampedCreateView,
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


class ContainerCreateView(PermissionRequiredMixin, UserStampedCreateView):
    model = Container
    template_name = "bins/container_form.html"
    permission_required = "bins.add_container"
    form_class = NewContainerForm
    success_url = reverse_lazy("bins:container_list")


class ContainerAttachmentCreateView(PermissionRequiredMixin, UserStampedCreateView):
    model = ContainerAttachment
    template_name = "bins/container_attachment_form.html"
    permission_required = "bins.containerattachment_add"
    form_class = ContainerAttachmentForm
    success_url = reverse_lazy("bins:container_list")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        request = self.request

        query_dict = request.GET

        container_params = {
            "container_id__exact": "id__exact",
            "container_id__iexact": "id__iexact",
        }

        for param in container_params:
            if param in query_dict:
                kwargs = {container_params[param]: query_dict[param]}
                try:
                    container_obj = Container.objects.get(**kwargs)
                    initial["container"] = str(container_obj.id)
                    messages.debug(request, f"Container found: {container_obj}")
                except ObjectDoesNotExist:
                    message = (
                        f"Container with {param}={query_dict[param]} does not exist."
                    )
                    messages.warning(request, message)
                break

        return initial


class ContainerAttachmentDeleteView(PermissionRequiredMixin, DeleteView):
    model = ContainerAttachment
    template_name = "bins/container_attachment_confirm_delete.html"
    permission_required = "bins.containerattachment_delete"
    success_url = reverse_lazy("bins:container_list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["container"] = self.object.container
        return context


class ContainerDeleteView(PermissionRequiredMixin, DeleteView):
    model = Container
    template_name = "bins/container_confirm_delete.html"
    permission_required = "bins.container_delete"
    success_url = reverse_lazy("bins:container_list")
