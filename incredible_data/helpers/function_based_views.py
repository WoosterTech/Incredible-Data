import abc
import logging
from collections.abc import Callable, Iterator
from http import HTTPMethod
from typing import (
    Any,
    Generic,
    SupportsIndex,
    TypeVar,
    overload,
    override,
)

from django.db import models
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.functional import Promise
from django.utils.safestring import SafeString

logger = logging.getLogger(__name__)


def generic_create_view(
    request: HttpRequest,
    form: type[BaseForm],
    template_name: str = "object_form.html",
    redirect: str | None = None,
) -> HttpResponseRedirect | HttpResponse:
    if request.method == HTTPMethod.POST:
        form_obj = form(request.POST)
        if form_obj.is_valid():
            # some stuff
            if redirect is None:
                redirect = "/"
            return HttpResponseRedirect(redirect)

    return render(request, template_name, {"form": form()})


class DetailWidget:
    field_name: str
    label: Promise | str | None
    empty_value: str
    linkify: bool | None
    template: str
    value_transform: Callable[[str], str] | None

    instance: models.Model | None
    field: models.Field | None  # pyright: ignore[reportMissingTypeArgument]

    def __init__(  # noqa: PLR0913
        self,
        field_name: str,
        label: Promise | str | None = None,
        empty_value: str = "--",
        value_transform: Callable[[str], str] | None = None,
        template: str = "field_base.html",
        linkify: bool | None = None,
    ) -> None:
        self.field_name = field_name
        self.label = label
        self.empty_value = empty_value
        self.linkify = linkify
        self.template = template
        self.value_transform = value_transform

        self.instance = None
        self.field = None

    @property
    def is_bound(self) -> bool:
        return self.instance is not None and self.field is not None  # pyright: ignore[reportUnknownMemberType]

    def bind(self, instance: models.Model) -> None:
        self.instance = instance
        model_cls = instance.__class__
        field_properties = model_cls._meta.get_field(self.field_name)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]  # noqa: SLF001
        if self.label is None:
            try:
                self.label = field_properties.verbose_name  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            except AttributeError as e:
                msg = f'{type(field_properties)} does not support "verbose_name"... please explore'  # pyright: ignore[reportUnknownArgumentType]  # noqa: E501
                raise AttributeError(msg) from e
        self.field = getattr(instance, self.field_name) or self.empty_value

        msg = f"Field: {self.field}<{type(self.field)}>"  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        logger.debug(msg)

    def generate_context(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        label = self.label
        field = (  # pyright: ignore[reportUnknownVariableType]
            self.field  # pyright: ignore[reportUnknownMemberType]
            if self.value_transform is None
            else self.value_transform(self.field)  # pyright: ignore[reportUnknownMemberType, reportArgumentType]
        )
        return {"label": label, "value": field}

    def render(self) -> SafeString:
        if not self.is_bound:
            msg = f"Field '{self.field_name}' must be bound before rendering."
            raise ValueError(msg)

        context = self.generate_context()

        return render_to_string(self.template, context=context)


_T = TypeVar("_T")


class CustomRoot(Generic[_T], abc.ABC):
    root: list[_T]

    def __init__(self, *fields: str | _T) -> None:
        root_list: list[_T] = []
        for field in fields:
            if isinstance(field, str):
                root_list.append(self.validate_field(field))
            else:
                root_list.append(field)
        self.root = root_list

    @classmethod
    @abc.abstractmethod
    def validate_field(cls, field: str) -> _T:
        raise NotImplementedError

    def __iter__(self) -> Iterator[_T]:
        return iter(self.root)

    @overload
    def __getitem__(self, item: SupportsIndex, /) -> _T: ...
    @overload
    def __getitem__(self, item: slice, /) -> list[_T]: ...
    def __getitem__(self, item: SupportsIndex | slice, /) -> _T | list[_T]:
        return self.root[item]

    def __setitem__(self, key: SupportsIndex, value: _T) -> None:
        self.root[key] = value


class DetailWidgets(CustomRoot[DetailWidget]):
    root: list[DetailWidget]

    @classmethod
    @override
    def validate_field(cls, field: str) -> DetailWidget:
        return DetailWidget(field_name=field)

    def bind(self, instance: models.Model) -> None:
        _bound_fields = [field.bind(instance) for field in self.root]

    def render_to_strings(self) -> list[SafeString]:
        return [field.render() for field in self.root]
