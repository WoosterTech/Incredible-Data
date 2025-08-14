from functools import lru_cache

def get_template_pack():  # -> Any:
    ...

TEMPLATE_PACK = ...

@lru_cache
def default_field_template(template_pack=...):  # -> _EngineTemplate:
    ...
def render_field(
    field,
    form,
    context,
    template=...,
    labelclass=...,
    layout_object=...,
    attrs=...,
    template_pack=...,
    extra_context=...,
    **kwargs,
): ...
def flatatt(attrs):  # -> SafeString:
    ...
def render_crispy_form(form, helper=..., context=...):  # -> SafeString:
    ...
def list_intersection(list1, list2):  # -> list[Any]:
    ...
def list_difference(left, right):  # -> list[Any]:
    ...
