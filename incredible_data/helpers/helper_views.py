import abc
from collections.abc import Iterable, Iterator
from typing import Any, cast, override

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import URLPattern, URLResolver, path
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django_tables2 import SingleTableView
from neapolitan.views import CRUDView, Role


class SingleTableListView(SingleTableView):
    """Adds context to SingleTableView for title and action buttons.

    view_title: title of table
    actions: list of 2-tuples "button label" and "url"

    Example:
    ```
    view_title = "Part Numbers"
    actions = [
        ("New Part Number", reverse_lazy("admin:app_partnumber_add")),
    ]
    ```
    """

    url_base: str | None = None
    lookup_url_kwarg: str | None = None
    lookup_field: str = "pk"
    path_converter: str = "int"

    view_title: str | None = None
    actions: list[tuple[str, str]] | None = None
    template_name: str | None = "base_list_tables2.html"

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # pyright: ignore[reportAny, reportExplicitAny]
        super_context = super().get_context_data(**kwargs)

        super_context["view_title"] = (
            self.view_title if self.view_title is not None else self.__class__.__name__
        )

        if self.actions is not None:
            super_context["action_links"] = [
                {"label": action[0], "href": action[1]} for action in self.actions
            ]

        return super_context


class ExtraContextDetailView(DetailView):  # pyright: ignore[reportMissingTypeArgument]
    """Adds context to DetailView for full detail URI."""

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # pyright: ignore[reportAny, reportExplicitAny]
        super_context = super().get_context_data(**kwargs)

        super_context["full_detail_uri"] = self.request.build_absolute_uri()

        return super_context


class UserStampedCreateView(CreateView):  # pyright: ignore[reportMissingTypeArgument]
    """Adds created_by and modified_by to initial data for CreateView."""

    @override
    def get_initial(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        initial = super().get_initial()

        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied

        assert not isinstance(user, AnonymousUser), "User must be authenticated."

        initial["created_by"] = str(user.pk)  # pyright: ignore[reportAny]
        initial["modified_by"] = str(user.pk)  # pyright: ignore[reportAny]

        return initial


class CustomCRUDView(CRUDView, abc.ABC):
    """Custom CRUDView that can be extended for specific models."""

    list_view: type[SingleTableListView] | None = None

    @classmethod
    def additional_urls(cls) -> list[URLPattern | URLResolver]:
        """Override this method to add custom URLs for the CRUDView."""
        return []

    @classmethod
    def _all_roles(cls) -> Iterator[Role]:
        return iter(Role)

    @classmethod
    def _get_list_pattern(cls) -> URLPattern:
        route_pattern = f"{cls.url_base}/"
        pattern_name: str = f"{cls.url_base}-list"

        assert cls.list_view is not None, "list_view for `_get_list_pattern`."

        return path(route_pattern, cls.list_view.as_view(), name=pattern_name)

    @override
    @classmethod
    def get_urls(
        cls, roles: Iterable[Role] | None = None
    ) -> list[URLPattern | URLResolver]:
        if roles is None:
            roles = cls._all_roles()
        list_pattern: URLPattern | None = None
        if cls.list_view is not None and Role.LIST in roles:
            list_pattern = cls._get_list_pattern()
            roles = [role for role in roles if role != Role.LIST]
        common = cast("list[URLPattern | URLResolver]", super().get_urls(roles=roles))  # pyright: ignore[reportUnknownMemberType]

        if list_pattern is not None:
            common.append(list_pattern)
        common.extend(cls.additional_urls())

        return common
