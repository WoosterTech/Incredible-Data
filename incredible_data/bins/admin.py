from django.contrib import admin

from incredible_data.contacts.admin import UserStampedModelAdmin

from .models import Container, ContainerStyle

# Register your models here.
admin.site.register(ContainerStyle)


@admin.register(Container)
class ContainerAdmin(UserStampedModelAdmin):
    list_display = ["id", "contents", "created_by"]
