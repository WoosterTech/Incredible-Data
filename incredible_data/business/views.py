import abc
import logging
from collections.abc import Iterable
from http import HTTPMethod
from typing import (
    Any,
    Generic,
    Protocol,
    TypedDict,
    TypeVar,
    cast,
    final,
    override,
    runtime_checkable,
)

from django import forms
from django.contrib import messages
from django.db import models
from django.db.models import Model
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import (
    path,
    reverse,
    reverse_lazy,  # pyright: ignore[reportAny]
)
from django.utils.functional import Promise
from django.utils.safestring import SafeString
from neapolitan.views import Role
from pydantic import BaseModel

from incredible_data.business.forms.business_accounting_forms import (
    InvoiceForm,
    OrderForm,
    ProjectForm,
)
from incredible_data.business.tables.business_accounting_tables import InvoiceTable
from incredible_data.business.tables.business_project_tables import (
    OrderTable,
    ProjectTable,
)
from incredible_data.helpers.function_based_views import (
    DetailWidget,
    DetailWidgets,
    generic_create_view,
)
from incredible_data.helpers.helper_views import CustomCRUDView, SingleTableListView

from .models.business_accounting_models import Invoice, Order
from .models.business_project_models import Project

logger = logging.getLogger(__name__)


# Create your views here.
def printable_invoice(request: HttpRequest, slug: str):
    invoice = (
        Invoice.objects.filter(slug=slug)
        .select_related("customer")
        .prefetch_related("invoiceline_set")
    )
    context = {"invoice": invoice.first()}
    return render(request, "business/invoice.html", context)


@final
class ProjectListView(SingleTableListView):
    view_title = "Projects"
    model = Project
    table_class = ProjectTable
    template_name = "base_list_tables2.html"
    actions = [("New", reverse_lazy("business:project-create"))]


def _get_project(slug: str) -> Project:
    return get_object_or_404(Project, slug=slug)


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


class ProjectDetailView(DetailView[Project]):
    pass


def project_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    project = _get_project(slug=slug)
    action_links: list[ActionLink] = [
        {
            "href": reverse("business:project-update", kwargs={"slug": slug}),
            "label": "Edit",
        },
        {"href": reverse("business:project-list"), "label": "List"},
    ]
    project_view = ProjectDetailView(
        Project,
        [
            DetailWidget("number"),
            DetailWidget("name"),
            DetailWidget("customer"),
            DetailWidget("notes", template="field_textarea.html"),
            DetailWidget("order"),
        ],
        action_links,
    )
    context = project_view.get_context(project)
    return render(request, "business/detail.html", context)


class InitialBase(BaseModel, abc.ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    pass


@runtime_checkable
class CRUDModel(Protocol):
    def get_absolute_url(self) -> str: ...


def process_form(
    request: HttpRequest,
    form_cls: type[forms.ModelForm],
    instance: models.Model | None = None,
    redirect_to: str | None = None,
) -> "HttpResponse":
    model = form_cls._meta.model  # noqa: SLF001
    assert model is not None, "Model is not defined"
    model_name = model.__name__
    form = (
        form_cls(request.POST, instance=instance)
        if instance is not None
        else form_cls(request.POST)
    )
    if form.is_valid():
        obj = cast("models.Model", form.save(commit=True))
        assert isinstance(obj, CRUDModel), (
            f"{model_name} does not have a get_absolute_url method"
        )
        redirect_url = redirect_to or obj.get_absolute_url()
        messages.info(request, f"{model_name} '{obj}' saved.")
        return redirect(redirect_url)

    return render(request, "object_form.html", {"form": form})


def get_next(params: dict[str, str | Any]) -> str:  # pyright: ignore[reportExplicitAny]
    next_url = params.pop("next", None)
    if isinstance(next_url, list):
        next_url = str(next_url[0])  # pyright: ignore[reportUnknownArgumentType]
    return next_url


def project_create_view(request: HttpRequest) -> HttpResponse:
    current_user = request.user
    initial: dict[str, str | list[str] | Any] = request.GET.dict()  # pyright: ignore[reportExplicitAny]
    next_url = get_next(initial)
    if request.method == HTTPMethod.POST:
        return process_form(request, ProjectForm, redirect_to=next_url)

    initial.update({"created_by": current_user.pk, "modified_by": current_user.pk})

    form = ProjectForm(initial=initial)

    return render(request, "object_form.html", {"form": form})


def project_edit_view(request: HttpRequest, slug: str) -> HttpResponse:
    current_user = request.user
    query_params: dict[str, str | list[str] | Any] = request.GET.dict()  # pyright: ignore[reportExplicitAny]
    next_url = get_next(query_params)
    project = _get_project(slug=slug)
    if request.method == HTTPMethod.POST:
        return process_form(
            request, ProjectForm, instance=project, redirect_to=next_url
        )

    query_params["modified_by"] = current_user.pk

    form = ProjectForm(instance=project, initial=query_params)

    return render(request, "object_form.html", {"form": form})


@final
class ProjectView(CustomCRUDView[Project]):
    model = Project
    fields = ["number", "name", "customer", "notes", "order"]
    lookup_field = "slug"
    path_converter = "slug"
    list_view = ProjectListView


def _get_order(slug: str) -> Order:
    return get_object_or_404(Order, slug=slug)


@final
class OrderListView(SingleTableListView):
    view_title = "Orders"
    model = Order
    table_class = OrderTable
    template_name = "base_list_tables2.html"
    actions = [("New", reverse_lazy("business:order-create"))]


class OrderDetailView(DetailView[Order]):
    pass


def order_create_view(request: HttpRequest) -> HttpResponse:
    current_user = request.user
    query_dict: dict[str, str | list[str] | Any] = request.GET.dict()  # pyright: ignore[reportExplicitAny]
    next_url = get_next(query_dict)
    if request.method == HTTPMethod.POST:
        return process_form(request, OrderForm, redirect_to=next_url)

    query_dict.update({"created_by": current_user.pk, "modified_by": current_user.pk})

    form = OrderForm(initial=query_dict)

    return render(request, "object_form.html", {"form": form})


def order_edit_view(request: HttpRequest, slug: str) -> HttpResponse:
    order = _get_order(slug)
    current_user = request.user
    query_dict: dict[str, str | list[str] | Any] = request.GET.dict()  # pyright: ignore[reportExplicitAny]
    redirect_to = get_next(query_dict)
    if request.method == HTTPMethod.POST:
        return process_form(request, OrderForm, instance=order, redirect_to=redirect_to)

    query_dict.update({"modified_by": current_user.pk})

    form = OrderForm(instance=order, initial=query_dict)

    return render(request, "object_form.html", {"form": form})


def order_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    order = _get_order(slug)

    action_links: list[ActionLink] = [
        {
            "href": reverse("business:order-update", args=(order.slug,)),  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            "label": "Edit",
        },
        {
            "href": order.get_create_project_url(),
            "label": "New Project",
        },
        {"href": reverse("business:order-list"), "label": "List"},
    ]
    order_view = OrderDetailView(
        Order,
        [
            "customer",
            "expected_date",
            DetailWidget("notes", template="field_textarea.html"),
        ],
        action_links,
    )
    context = order_view.get_context(order)

    return render(request, "business/detail.html", context)


@final
class OrderView(CustomCRUDView[Order]):
    model = Order
    fields = ["customer", "expected_date", "notes"]
    lookup_field = "slug"
    path_converter = "slug"
    list_view = OrderListView


def _get_invoice(slug: str) -> Invoice:
    return get_object_or_404(Invoice, slug=slug)


@final
class InvoiceListView(SingleTableListView):
    view_title = "Invoices"
    model = Invoice
    table_class = InvoiceTable
    template_name = "base_list_tables2.html"
    actions = [("New", reverse_lazy("business:invoice-create"))]


def invoice_create_view(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    template_name = "object_form.html"
    form = InvoiceForm
    redirect = "/"
    return generic_create_view(
        request, template_name=template_name, redirect=redirect, form=form
    )


class InvoiceDetailView(DetailView[Invoice]): ...


def invoice_detail_view(request: HttpRequest, slug: str) -> HttpResponse:
    invoice = _get_invoice(slug)
    action_links: list[ActionLink] = [
        {
            "href": reverse("admin:business_invoice_change", args=(invoice.pk,)),  # pyright: ignore[reportAny]
            "label": "Edit",
        },
        {"href": reverse("business:invoice-list"), "label": "List"},
        {
            "href": reverse("business:invoice_detail_printable", kwargs={"slug": slug}),
            "label": "Printable",
        },
    ]
    fields = DetailWidgets(
        "number",
        "customer",
        DetailWidget("status", value_transform=lambda v: v.title()),
        "due_date",
        "subtotal",
        "grand_total",
        "order",
        DetailWidget("notes", template="field_textarea.html"),
        DetailWidget("terms", template="field_textarea.html"),
        "status_changed",
    )
    invoice_view = InvoiceDetailView(Invoice, fields.root, action_links)
    context = invoice_view.get_context(invoice)

    return render(request, "business/detail.html", context)


@final
class InvoiceView(CustomCRUDView[Invoice]):
    model = Invoice
    fields = [
        "number",
        "status",
        "customer",
        "terms",
        "notes",
        "grand_total",
        "due_date",
        "order",
    ]
    lookup_field: str = "slug"
    path_converter: str = "slug"
    list_view = InvoiceListView

    @override
    @classmethod
    def additional_urls(cls):
        urls = super().additional_urls()
        detail_url = Role.DETAIL.url_pattern(cls)
        printable_url = path(
            detail_url + "printable/",
            printable_invoice,
            name="invoice_printable",
        )

        urls.append(printable_url)
        return urls

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # pyright: ignore[reportAny, reportExplicitAny]
        context = cast("dict[str, Any]", super().get_context_data(**kwargs))  # pyright: ignore[reportAny, reportExplicitAny]

        lookup_value = getattr(self.object, self.lookup_field)  # pyright: ignore[reportAny]
        printable_action = {
            "label": "Printable Invoice",
            "href": reverse(
                "business:invoice_printable", kwargs={self.lookup_field: lookup_value}
            ),
        }
        action_links = cast("list[dict[str,str]]", context.get("action_links", []))
        if self.role == Role.DETAIL:
            action_links.append(printable_action)
        context["action_links"] = action_links

        return context
