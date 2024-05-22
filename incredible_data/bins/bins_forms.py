from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models.bins_container_models import Container


class NewContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ["id", "contents", "image", "style"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "new-container-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "bins:container_add"

        self.helper.add_input(Submit("submit", "Submit"))
