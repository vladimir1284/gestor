from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Submit
from django import forms

from rent.forms.lease import AppendedText
from rent.forms.lease import PrependedText
from rent.models.guarantor import Guarantor


class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = [
            "guarantor_avatar",
            "guarantor_name",
            "guarantor_license",
            "guarantor_license_file",
            "guarantor_address",
            "guarantor_email",
            "guarantor_phone_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["guarantor_license_file"].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        HTML(
                            """
                        {% load static %}
                        <img id="guarantor_preview"
                        alt="user-avatar"
                        class="d-block rounded"
                        height="100" width="100"
                        {% if form.avatar.value %}
                            src="/media/{{ form.avatar.value }}"
                        {% else %}
                            src="{% static 'assets/img/icons/user.png' %}"
                        {% endif %}>
                        """
                        ),
                        css_class="d-flex align-items-start align-items-sm-center gap-4",
                    ),
                    Div(
                        Div(
                            AppendedText(
                                "guarantor_avatar",
                                mark_safe("<i class='bx bx-image' ></i>"),
                            ),
                        ),
                        css_class="mb-3",
                    ),
                ),
                Div(
                    PrependedText(
                        "guarantor_name", mark_safe("<i class='bx bx-user' ></i>")
                    ),
                    css_class="mb-3",
                ),
                Div(
                    PrependedText(
                        "guarantor_license", mark_safe("<i class='bx bx-id-card' ></i>")
                    ),
                    css_class="mb-3",
                ),
                Div(
                    AppendedText(
                        "guarantor_license_file",
                        mark_safe("<i class='bx bx-id-card' ></i>"),
                    ),
                    css_class="mb-3",
                ),
                Div(
                    PrependedText(
                        "guarantor_address", mark_safe("<i class='bx bx-home' ></i>")
                    ),
                    css_class="mb-3",
                ),
                Div(
                    PrependedText(
                        "guarantor_email", mark_safe("<i class='bx bx-envelope' ></i>")
                    ),
                    css_class="mb-3",
                ),
                Div(
                    PrependedText(
                        "guarantor_phone_number",
                        mark_safe("<i class='bx bx-phone' ></i>"),
                    ),
                    css_class="mb-3",
                ),
                ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
                css_class="mb-3",
            ),
        )
