import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from incredible_data.business.models.business_project_models import Project


class ProjectTable(tables.Table):
    number = tables.Column(_("number"), linkify=True)

    class Meta:
        model = Project
        fields = ["number", "name"]
