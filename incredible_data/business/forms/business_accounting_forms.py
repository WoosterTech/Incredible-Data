from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from incredible_data.business.models.business_accounting_models import Invoice


class InvoiceForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"

        self.helper.add_input(Submit("submit", "Submit"))
