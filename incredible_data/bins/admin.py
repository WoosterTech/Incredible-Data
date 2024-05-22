from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from import_export.admin import ImportExportMixin

from incredible_data.bins.resources import ContainerResource
from incredible_data.contacts.admin import UserStampedModelAdmin

from .models.bins_container_models import Container, ContainerAttachment, ContainerStyle

# Register your models here.
admin.site.register(ContainerStyle)


@admin.register(ContainerAttachment)
class ContainerAttachmentAdmin(UserStampedModelAdmin):
    list_display = [
        "name",
        "attachment",
        "attachment_type",
        "primary",
        "created_by_name",
    ]
    search_fields = ["name", "attachment", "attachment_type"]
    list_filter = ["attachment_type", "primary"]
    list_select_related = ["created_by"]
    list_per_page = 20
    list_max_show_all = 100
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "container",
                    "attachment",
                    "attachment_type",
                    "primary",
                ]
            },
        ),
        (
            "Audit",
            {"fields": ["created_by", "modified_by", "name"], "classes": ["collapse"]},
        ),
    ]

    def get_changeform_initial_data(
        self, request: HttpRequest
    ) -> dict[str, str | list[str]]:
        initial = super().get_changeform_initial_data(request)

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


class ContainerAttachmentInline(admin.TabularInline):
    model = ContainerAttachment
    extra = 1
    fields = ["attachment", "attachment_type", "primary", "created_by", "modified_by"]


@admin.register(Container)
class ContainerAdmin(UserStampedModelAdmin, ImportExportMixin):
    list_display = ["id", "contents", "created_by_name"]
    search_fields = ["id", "contents"]
    inlines = [ContainerAttachmentInline]
    resource_classes = [ContainerResource]
