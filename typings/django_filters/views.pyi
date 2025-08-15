from django.views.generic import View
from django.views.generic.list import (
    MultipleObjectMixin,
    MultipleObjectTemplateResponseMixin,
)

class FilterMixin:
    filterset_class = ...
    filterset_fields = ...
    strict = ...
    def get_filterset_class(self):  # -> type[FilterSet]:
        ...
    def get_filterset(self, filterset_class): ...
    def get_filterset_kwargs(self, filterset_class):  # -> dict[str, Any | None]:
        ...
    def get_strict(self):  # -> bool:
        ...

class BaseFilterView(FilterMixin, MultipleObjectMixin, View):
    def get(self, request, *args, **kwargs): ...

class FilterView(MultipleObjectTemplateResponseMixin, BaseFilterView):
    template_name_suffix = ...

def object_filter(
    request,
    model=...,
    queryset=...,
    template_name=...,
    extra_context=...,
    context_processors=...,
    filter_class=...,
):  # -> HttpResponse:
    ...
