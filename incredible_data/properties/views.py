from django.views.generic import ListView

from incredible_data.properties.models.properties_models import Property


# Create your views here.
class PropertyListView(ListView):
    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    paginate_by = 10
    ordering = ["-created"]
