from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from .models import Customer


class UserStampedModelAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    def get_changeform_initial_data(
        self, request: HttpRequest
    ) -> dict[str, str | list[str]]:
        initial = super().get_changeform_initial_data(request)

        user = request.user

        if not user.is_authenticated:
            raise PermissionDenied

        initial["created_by"] = str(user.id)
        initial["modified_by"] = str(user.id)

        return initial


def get_logged_in_user(request: HttpRequest) -> str:
    user = request.user
    if not user.is_authenticated:
        raise PermissionDenied

    return str(user.id)


@admin.register(Customer)
class CustomerAdmin(UserStampedModelAdmin):
    list_display = ["name"]
