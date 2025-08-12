from typing import Generic, TypeVar, override

from django.contrib.admin import AdminSite, ModelAdmin, TabularInline
from django.db.models import Model
from django.db.models.options import Options

_ModelT = TypeVar("_ModelT", bound=Model)

class GenericModelAdmin(ModelAdmin[_ModelT], Generic[_ModelT]):
    add_form_template: str | None = None  # pyright: ignore[reportIncompatibleVariableOverride]
    opts: Options[_ModelT]

    @override
    def get_view_on_site_url(self, obj: _ModelT | None = None) -> str | None: ...

class UserStampedAdmin(GenericModelAdmin[_ModelT], Generic[_ModelT]):
    model: type[_ModelT]

    def __init__(self, model: type[_ModelT], admin_site: AdminSite | None) -> None: ...

class GenericTabularInline(TabularInline[_ModelT], Generic[_ModelT]): ...
