from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms

from services.models import Associated


class LesseeContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["phone_number"].required = True
        self.fields["language"].required = True
        self.fields["email"].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(Field("name"), css_class="mb-2"),
            Div(Field("phone_number"), css_class="mb-2"),
            Div(Field("language"), css_class="mb-2"),
            Div(Field("email"), css_class="mb-2"),
            ButtonHolder(
                Submit(
                    "submit",
                    "Next",
                    css_class="btn btn-success",
                ),
                # css_class="position-absolute top-0 end-0 pt-3 pe-3",
            ),
        )

    class Meta:
        model = Associated
        fields = ("name", "phone_number", "language", "email")
