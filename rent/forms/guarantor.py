from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from django import forms

from rent.forms.lease import PrependedText
from rent.models.guarantor import Guarantor


class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = [
            "guarantor_name",
            "guarantor_license",
            "guarantor_address",
            "guarantor_email",
            "guarantor_phone_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                PrependedText(
                    "guarantor_name", mark_safe("<i class='bx bx-user' ></i>")
                ),
                PrependedText(
                    "guarantor_license", mark_safe("<i class='bx bx-id-card' ></i>")
                ),
                PrependedText(
                    "guarantor_address", mark_safe("<i class='bx bx-home' ></i>")
                ),
                PrependedText(
                    "guarantor_email", mark_safe("<i class='bx bx-envelope' ></i>")
                ),
                PrependedText(
                    "guarantor_phone_number", mark_safe("<i class='bx bx-phone' ></i>")
                ),
                css_class="mb-3",
            ),
        )
