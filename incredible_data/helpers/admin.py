# pyright: reportMissingTypeArgument = warning
"""This module provides generic admin classes for Django models as well as a UserStampedAdmin class."""

from collections.abc import Iterable
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypedDict,
    TypeVar,
    cast,
    overload,
    override,
)

from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.admin.helpers import AdminForm, InlineAdminFormSet
from django.contrib.admin.options import (
    IS_POPUP_VAR,
    TO_FIELD_VAR,
    get_content_type_for_model,
)
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.db.models import Model
from django.db.models.options import Options
from django.forms import ModelForm
from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.http import HttpRequest

    from incredible_data.users.models import User

_ModelT = TypeVar("_ModelT", bound=Model)

if TYPE_CHECKING:
    ModelOptions = Options
else:

    class ModelOptions(Options, Generic[_ModelT]):
        pass


class ModelAdminContext(TypedDict, Generic[_ModelT]):
    add: bool
    change: bool
    has_view_permission: bool
    has_add_permission: bool
    has_change_permission: bool
    has_delete_permission: bool
    has_editable_inline_admin_formsets: bool
    has_file_field: bool
    has_absolute_url: bool
    absolute_url: str | None
    form_url: str
    opts: ModelOptions[_ModelT]
    content_type_id: str
    save_as: bool
    save_on_top: bool
    to_field_var: str
    is_popup_var: str
    app_label: str
    adminform: "GenericModelAdmin[_ModelT]"
    inline_admin_formsets: list[InlineAdminFormSet]


class GenericModelAdmin(ModelAdmin, Generic[_ModelT]):  # pyright: ignore[reportMissingTypeArgument]
    class Meta:
        abstract: bool = True


class GenericTabularInline(TabularInline, Generic[_ModelT]):  # pyright: ignore[reportMissingTypeArgument]
    class Meta:
        abstract: bool = True


class GenericAdminForm(AdminForm, Generic[_ModelT]):
    prepopulated_fields: dict[str, Any]  # pyright: ignore[reportExplicitAny]
    model_admin: GenericModelAdmin[_ModelT]
    readonly_fields: Iterable[str]


class UserStampedAdmin(GenericModelAdmin[_ModelT], Generic[_ModelT]):
    created_by_field: str = "created_by"
    opts: "Options[_ModelT]"

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        abstract: bool = True

    @override
    def save_model(
        self, request: "HttpRequest", obj: _ModelT, form: ModelForm, change: bool
    ) -> None:
        user = cast("User", request.user)
        if not change:
            setattr(obj, self.created_by_field, user)

        super().save_model(request, obj, form, change)  # pyright: ignore[reportUnknownMemberType]

    def _has_editable_inline_admin_formsets(
        self, context: ModelAdminContext[_ModelT]
    ) -> bool:
        formsets = context["inline_admin_formsets"]
        for inline in formsets:
            if (
                inline.has_add_permission  # pyright: ignore[reportAny]
                or inline.has_change_permission  # pyright: ignore[reportAny]
                or inline.has_delete_permission  # pyright: ignore[reportAny]
            ):
                return True
        return False

    def _any_formset_is_multipart(self, formsets: list[InlineAdminFormSet]) -> bool:
        return any(formset.formset.is_multipart() for formset in formsets)  # pyright: ignore[reportAny]

    def _has_file_field(self, context: ModelAdminContext[_ModelT]) -> bool:
        admin_form = context["adminform"]
        inline_formsets = context["inline_admin_formsets"]
        return admin_form.form.is_multipart() or self._any_formset_is_multipart(  # pyright: ignore[reportCallIssue, reportUnknownVariableType]
            inline_formsets
        )

    @override
    def render_change_form(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: "HttpRequest",
        context: ModelAdminContext[_ModelT],
        add: bool = False,
        change: bool = False,
        form_url: str = "",
        obj: _ModelT | None = None,
    ) -> TemplateResponse:
        app_label = self.opts.app_label
        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters(
            {"preserved_filters": preserved_filters, "opts": self.opts}, url=form_url
        )
        view_on_site_url = self.get_view_on_site_url(obj)  # pyright: ignore[reportUnknownMemberType]
        has_editable_inline_admin_formsets = self._has_editable_inline_admin_formsets(
            context
        )

        context.update(
            {
                "add": add,
                "change": change,
                "has_view_permission": self.has_view_permission(request, obj),  # pyright: ignore[reportUnknownMemberType]
                "has_add_permission": self.has_add_permission(request),
                "has_change_permission": self.has_change_permission(request, obj),  # pyright: ignore[reportUnknownMemberType]
                "has_delete_permission": self.has_delete_permission(request, obj),  # pyright: ignore[reportUnknownMemberType]
                "has_editable_inline_admin_formsets": has_editable_inline_admin_formsets,
                "has_file_field": self._has_file_field(context),
                "has_absolute_url": view_on_site_url is not None,
                "absolute_url": view_on_site_url,
                "form_url": form_url,
                "opts": self.opts,
                "content_type_id": get_content_type_for_model(self.model).pk,  # pyright: ignore[reportUnknownMemberType, reportAny, reportUnknownArgumentType]
                "save_as": self.save_as,
                "save_on_top": self.save_on_top,
                "to_field_var": TO_FIELD_VAR,
                "is_popup_var": IS_POPUP_VAR,
                "app_label": app_label,
            }
        )
        form_template = (
            self.add_form_template
            if (add and self.add_form_template is not None)  # pyright: ignore[reportUnnecessaryComparison]
            else self.change_form_template
        )

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            template=self._get_template(form_template),
            context=context,  # pyright: ignore[reportArgumentType]
        )

    @overload
    def _get_template(self, form_template: str) -> str: ...
    @overload
    def _get_template(self, form_template: None) -> list[str]: ...
    @overload
    def _get_template(self, form_template: str | None) -> str | list[str]: ...
    def _get_template(self, form_template: str | None) -> str | list[str]:
        if form_template is not None:
            return form_template
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        return [
            f"admin/{app_label}/{model_name}/change_form.html",
            f"admin/{app_label}/change_form.html",
            "admin/change_form.html",
        ]
