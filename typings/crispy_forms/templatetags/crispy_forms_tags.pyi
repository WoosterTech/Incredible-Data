from functools import lru_cache

from crispy_forms.templatetags.crispy_forms_filters import *  # noqa: F403
from django import template

register = ...

class ForLoopSimulator:
    def __init__(self, formset) -> None: ...
    def iterate(self):  # -> None:
        ...

class BasicNode(template.Node):
    def __init__(self, form, helper, template_pack=...) -> None: ...
    def get_render(self, context): ...
    def get_response_dict(
        self, helper, context, is_formset
    ):  # -> dict[str, Any | dict[Any, Any] | bool | str | SafeString | None]:
        ...

@lru_cache
def whole_uni_formset_template(template_pack=...):  # -> _EngineTemplate:
    ...
@lru_cache
def whole_uni_form_template(template_pack=...):  # -> _EngineTemplate:
    ...

class CrispyFormNode(BasicNode):
    def render(self, context):  # -> SafeString:
        ...

@register.tag(name="crispy")
def do_uni_form(parser, token):  # -> CrispyFormNode:
    ...
