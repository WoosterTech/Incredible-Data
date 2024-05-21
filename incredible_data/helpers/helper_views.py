from typing import Any

from django.views.generic.detail import DetailView
from django_tables2 import SingleTableView


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

    view_title: str | None = None
    actions: list[tuple[str, str]] | None = None
    template_name = "base_list_tables2.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        super_context = super().get_context_data(**kwargs)

        super_context["view_title"] = (
            self.view_title if self.view_title is not None else self.__class__.__name__
        )

        if self.actions is not None:
            super_context["action_links"] = [
                {"label": action[0], "href": action[1]} for action in self.actions
            ]

        return super_context


class ExtraContextDetailView(DetailView):
    """Adds context to DetailView for full detail URI."""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        super_context = super().get_context_data(**kwargs)

        super_context["full_detail_uri"] = self.request.build_absolute_uri()

        return super_context
