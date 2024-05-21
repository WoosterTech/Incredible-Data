from django.contrib import admin
from import_export.admin import ImportExportMixin

from incredible_data.bins.resources import ContainerResource
from incredible_data.contacts.admin import UserStampedModelAdmin

from .models.bins_container_models import Container, ContainerStyle

# Register your models here.
admin.site.register(ContainerStyle)


@admin.register(Container)
class ContainerAdmin(UserStampedModelAdmin, ImportExportMixin):
    list_display = ["id", "contents", "created_by_name"]
    resource_classes = [ContainerResource]
