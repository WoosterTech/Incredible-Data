# Create your views here.
import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Generic, TypedDict, TypeVar, cast

from django.contrib import messages
from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.functional import Promise
from django.utils.safestring import SafeString

from incredible_data.customers.filters import CustomerFilter
from incredible_data.customers.forms import CustomerForm
from incredible_data.customers.models import Customer
from incredible_data.customers.tables import CustomerTable
from incredible_data.helpers.function_based_views import (
    DetailWidget,
    DetailWidgets,
)

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

_T = TypeVar("_T", bound=Model)


class ActionLink(TypedDict):
    href: str
    label: str | Promise


class DetailView(Generic[_T]):
    model: type[_T]
    fields: DetailWidgets
    actions: list[ActionLink]

    def __init__(
        self,
        model: type[_T],
        fields: Iterable[str | DetailWidget],
        actions: Iterable[ActionLink],
    ) -> None:
        self.model = model
        self.fields = DetailWidgets(*fields)
        self.actions = list(actions)

    def render_fields(self, instance: _T) -> list[SafeString]:
        self.fields.bind(instance)
        return self.fields.render_to_strings()

    def get_context(self, instance: _T, *args: Any, **kwargs: Any) -> dict[str, Any]:  # pyright: ignore[reportAny, reportExplicitAny, reportUnusedParameter]
        context: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
        context["action_links"] = self.actions
        context["fields"] = self.render_fields(instance)
        context["object"] = instance
        context["object_context_name"] = self.model.__name__.lower()

        model_name = self.model.__name__.lower()
        context[model_name] = instance

        return context


def customer_list_view(request: "HttpRequest") -> "HttpResponse":
    f = CustomerFilter(request.GET)
    qs = cast("QuerySet[Customer]", f.qs)
    table = CustomerTable(qs)
    action_links = [
        {
            "href": reverse("customers:customer-create"),
            "label": "Create",
        },
    ]
    return render(
        request,
        "base_list_tables2.html",
        {"filter": f, "table": table, "action_links": action_links},
    )


def customer_detail_view(request: "HttpRequest", slug: str) -> "HttpResponse":
    customer = get_object_or_404(Customer, slug=slug)
    action_links: list[ActionLink] = [
        {
            "href": reverse("customers:customer-update", kwargs={"slug": slug}),
            "label": "Edit",
        },
        {
            "href": customer.get_create_order_url(),
            "label": "New Order",
        },
        {"href": reverse("customers:customer-list"), "label": "List"},
    ]
    customer_view = DetailView[Customer](
        Customer,
        [
            DetailWidget("name"),
            DetailWidget("main_phone"),
        ],
        action_links,
    )
    context = customer_view.get_context(customer)
    return render(request, "business/detail.html", context)


def customer_edit_view(request: "HttpRequest", slug: str) -> "HttpResponse":
    current_user = request.user
    customer = get_object_or_404(Customer, slug=slug)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            saved_customer = cast("Customer", form.save(commit=True))
            redirect_url = saved_customer.get_absolute_url()
            messages.info(request, f"Customer '{saved_customer}' updated.")
            return redirect(redirect_url)

        return render(request, "object_form.html", {"form": form})

    form = CustomerForm(instance=customer, initial={"modified_by": current_user})

    return render(request, "object_form.html", {"form": form})


def customer_create_view(request: "HttpRequest") -> "HttpResponse":
    current_user = request.user
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            new_customer = cast("Customer", form.save(commit=True))
            redirect_url = new_customer.get_absolute_url()
            messages.info(request, f"Customer '{new_customer}' created.")
            return redirect(redirect_url)

        return render(request, "object_form.html", {"form": form})

    form = CustomerForm(
        initial={"created_by": current_user, "modified_by": current_user}
    )
    return render(request, "object_form.html", {"form": form})
