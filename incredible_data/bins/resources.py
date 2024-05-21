from import_export import resources

from .models.bins_container_models import Container


class ContainerResource(resources.ModelResource):
    class Meta:
        model = Container
        fields = ("id", "contents", "image", "style", "slug")
        export_order = ("id", "contents", "image", "style", "slug")
