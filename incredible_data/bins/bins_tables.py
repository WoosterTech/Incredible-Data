import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from .models.bins_container_models import Container


class ContainerTable(tables.Table):
    id = tables.Column(_("ID"), linkify=True)
    created_by_name = tables.Column(_("Created By"), accessor="created_by__name")

    class Meta:
        model = Container
        fields = ("id", "contents", "created_by_name")
        export_order = ("id", "contents", "created_by_name")
        attrs = {"class": "table table-striped table-bordered"}
