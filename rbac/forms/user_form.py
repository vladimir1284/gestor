from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from django import forms
from django.contrib.auth.models import Group
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
        self.fields["groups"] = forms.ModelMultipleChoiceField(
            queryset=Group.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="",
        )
        # self.fields["groups"].label = "Roles"
        # self.fields["groups"].widget = forms.CheckboxSelectMultiple()
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
            # Div(
            #     Field(
            #         "groups",
            #         # PrependedText(
            #         #     "groups",
            #         #     mark_safe('<i class="bx bx-cog"></i>'),
            #         # )
            #     ),
            #     css_class="row mb-3",
            # ),
            Div(
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
                            <button
                            data-bs-target="#groups"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                Roles
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            Field("groups"),
                            css_class="accordion-body",
                        ),
                        css_id="groups",
                        css_class="accordion-collapse collapse",
                    ),
                    css_id="groups-accordion",
                    css_class="accordion-item border-bottom",
                ),
                css_id="others-accordion",
                css_class="accordion mb-4 border rounded",
            ),
            # ButtonHolder(
            #     Submit(
            #         "submit",
            #         "Enviar",
            #         css_class="btn btn-success",
            #     ),
            # ),
        )
