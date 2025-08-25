from typing import final

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from incredible_data.customers.models import Customer


@final
class CustomerForm(forms.ModelForm):
    @final
    class Meta:
        model = Customer
        fields = ["name", "main_phone", "created_by", "modified_by"]

    def __init__(self, *args, **kwargs) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            "main_phone",
            Field("created_by", type="hidden"),
            Field("modified_by", type="hidden"),
        )

        self.helper.add_input(Submit("submit", _("Submit")))
