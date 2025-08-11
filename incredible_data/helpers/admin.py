from typing import TYPE_CHECKING, Generic, TypeVar, cast, override

from django.contrib.admin import ModelAdmin
from django.db.models import Model
from django.forms import ModelForm

if TYPE_CHECKING:
    from django.http import HttpRequest

    from incredible_data.users.models import User

_ModelT = TypeVar("_ModelT", bound=Model)


class UserStampedAdmin(ModelAdmin, Generic[_ModelT]):  # pyright: ignore[reportMissingTypeArgument]
    created_by_field: str = "created_by"

    class Meta:
        abstract: bool = True

    @override
    def save_model(
        self, request: "HttpRequest", obj: _ModelT, form: ModelForm, change: bool
    ) -> None:
        user = cast("User", request.user)
        if not change:
            setattr(obj, self.created_by_field, user)

        super().save_model(request, obj, form, change)  # pyright: ignore[reportUnknownMemberType]
