# pyright: reportMissingTypeArgument=false

import logging
from typing import TYPE_CHECKING, Any, cast, final, override

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Row, Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from incredible_data.business.models.business_accounting_models import Invoice, Order
from incredible_data.business.models.business_project_models import Project

if TYPE_CHECKING:
    from incredible_data.customers.models import Customer

logger = logging.getLogger(__name__)


@final
class InvoiceForm(forms.ModelForm):
    @final
    class Meta:
        model = Invoice
        fields = [
            "status",
            "customer",
            "terms",
            "notes",
            "grand_total",
            "due_date",
            "order",
        ]

    def __init__(self, *args, **kwargs):  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))


@final
class CustomerWidget(ModelSelect2Widget):
    search_fields = ["name__icontains"]
    # TODO: Add queryset to select customer for better performance


@final
class OrderForm(forms.ModelForm):
    @final
    class Meta:
        model = Order
        fields = ["customer", "expected_date", "notes", "created_by", "modified_by"]
        widgets = {
            "customer": CustomerWidget(
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select a Customer",
                },
            ),
            "expected_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "customer",
            "expected_date",
            "notes",
            Field("created_by", type="hidden"),
            Field("modified_by", type="hidden"),
        )

        self.helper.add_input(Submit("submit", _("Submit")))


@final
class OrderWidget(ModelSelect2Widget):
    search_fields = ["customer__name__icontains"]
    # TODO: Add queryset to select customer for better performance


@final
class ProjectForm(forms.ModelForm):
    @final
    class Meta:
        model = Project
        fields = ["name", "customer", "order", "notes", "created_by", "modified_by"]
        widgets = {
            "customer": CustomerWidget(
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select a Customer",
                },
            ),
            "order": OrderWidget(
                dependent_fields={"customer": "customer"},
                attrs={
                    "data-minimum-input-length": 0,
                    "data-placeholder": "Select an Order",
                },
            ),
        }

    def __init__(self, *args, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]

        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            Row("customer", "order"),
            "notes",
            Field("created_by", type="hidden"),
            Field("modified_by", type="hidden"),
        )

        self.helper.add_input(Submit("submit", _("Submit")))

    @override
    def clean(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        cleaned_data = super().clean()
        customer = cast("Customer", cleaned_data["customer"])
        order = cast("Order | None", cleaned_data.get("order", None))
        if order is not None:
            if customer != order.customer:  # pyright: ignore[reportUnknownMemberType]
                msg = f"Order '{order}' is not for customer '{customer}'"
                raise forms.ValidationError(msg)

        return cleaned_data
