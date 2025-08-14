from .layout import Div, Field, LayoutObject, TemplateNameMixin

class PrependedAppendedText(Field):
    template = ...
    def __init__(
        self,
        field,
        prepended_text=...,
        appended_text=...,
        input_size=...,
        *,
        active=...,
        css_class=...,
        wrapper_class=...,
        template=...,
        **kwargs,
    ) -> None: ...
    def render(self, form, context, template_pack=..., extra_context=..., **kwargs): ...

class AppendedText(PrependedAppendedText):
    def __init__(
        self,
        field,
        text,
        *,
        input_size=...,
        active=...,
        css_class=...,
        wrapper_class=...,
        template=...,
        **kwargs,
    ) -> None: ...

class PrependedText(PrependedAppendedText):
    def __init__(
        self,
        field,
        text,
        *,
        input_size=...,
        active=...,
        css_class=...,
        wrapper_class=...,
        template=...,
        **kwargs,
    ) -> None: ...

class FormActions(LayoutObject):
    template = ...
    def __init__(
        self, *fields, css_id=..., css_class=..., template=..., **kwargs
    ) -> None: ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class InlineCheckboxes(Field):
    template = ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class InlineRadios(Field):
    template = ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class FieldWithButtons(Div):
    template = ...
    field_template = ...
    def __init__(
        self, *fields, input_size=..., css_id=..., css_class=..., template=..., **kwargs
    ) -> None: ...
    def render(self, form, context, template_pack=..., extra_context=..., **kwargs): ...

class StrictButton(TemplateNameMixin):
    template = ...
    field_classes = ...
    def __init__(
        self, content, css_id=..., css_class=..., template=..., **kwargs
    ) -> None: ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class Container(Div):
    css_class = ...
    def __init__(
        self,
        name,
        *fields,
        css_id=...,
        css_class=...,
        template=...,
        active=...,
        **kwargs,
    ) -> None: ...
    def __contains__(self, field_name):  # -> bool:
        ...

class ContainerHolder(Div):
    def first_container_with_errors(self, errors):  # -> None:
        ...
    def open_target_group_for_form(self, form): ...

class Tab(Container):
    css_class = ...
    link_template = ...
    def render_link(self, template_pack=..., **kwargs):  # -> SafeString:
        ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class TabHolder(ContainerHolder):
    template = ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class AccordionGroup(Container):
    template = ...
    data_parent = ...

class Accordion(ContainerHolder):
    template = ...
    def __init__(
        self, *accordion_groups, css_id=..., css_class=..., template=..., **kwargs
    ) -> None: ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class Alert(Div):
    template = ...
    css_class = ...
    def __init__(
        self,
        content,
        dismiss=...,
        block=...,
        css_id=...,
        css_class=...,
        template=...,
        **kwargs,
    ) -> None: ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...

class UneditableField(Field):
    template = ...
    def __init__(
        self, field, css_class=..., wrapper_class=..., template=..., **kwargs
    ) -> None: ...

class InlineField(Field):
    template = ...

class Modal(LayoutObject):
    template = ...
    def __init__(
        self,
        *fields,
        template=...,
        css_id=...,
        title=...,
        title_id=...,
        css_class=...,
        title_class=...,
        **kwargs,
    ) -> None: ...
    def render(self, form, context, template_pack=..., **kwargs):  # -> SafeString:
        ...
