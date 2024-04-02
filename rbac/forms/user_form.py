from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "groups",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].label = "Roles"
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText(
                        "username",
                        mark_safe('<i class="bx bx-user-circle"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "first_name",
                        mark_safe('<i class="bx bx-user"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "last_name",
                        mark_safe('<i class="bx bx-user"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "groups",
                        mark_safe('<i class="bx bx-cog"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            # ButtonHolder(
            #     Submit(
            #         "submit",
            #         "Enviar",
            #         css_class="btn btn-success",
            #     ),
            # ),
        )
