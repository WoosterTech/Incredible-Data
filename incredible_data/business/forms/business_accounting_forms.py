# pyright: reportMissingTypeArgument=false
from typing import TYPE_CHECKING, cast, final, override

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from incredible_data.business.models.business_accounting_models import Invoice
from incredible_data.business.models.business_project_models import Project

if TYPE_CHECKING:
    from incredible_data.business.models.business_accounting_models import Order
    from incredible_data.customers.models import Customer


@final
class InvoiceForm(forms.ModelForm):
    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
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
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))


@final
class ProjectForm(forms.ModelForm):
    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Project
        fields = ["name", "customer", "notes", "order", "created_by", "modified_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            "customer",
            "notes",
            "order",
            Field("created_by", type="hidden"),
            Field("modified_by", type="hidden"),
        )

        self.helper.add_input(Submit("submit", _("Submit")))

    @override
    def clean(self):
        data = self.cleaned_data
        customer = cast("Customer", data["customer"])
        order = cast("Order | None", data.get("order", None))
        if order is not None:
            if customer != order.customer:  # pyright: ignore[reportUnknownMemberType]
                msg = f"Order '{order}' is not for customer '{customer}'"
                raise forms.ValidationError(msg)
