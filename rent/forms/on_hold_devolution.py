from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Submit
from django import forms

from rent.models.trailer_deposit import TrailerDeposit


class OnHoldReturnForm(forms.ModelForm):
    class Meta:
        model = TrailerDeposit
        fields = ["returned_amount", "returned_note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["returned_amount"].label = "To return"
        self.fields["returned_note"].label = "Note"
        self.fields["returned_note"].widget.attrs["rows"] = 3

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                PrependedText(
                    "returned_amount",
                    mark_safe("<i class='bx bx-dollar' ></i>"),
                ),
                css_class="mb-3",
            ),
            Div(
                PrependedText(
                    "returned_note",
                    mark_safe("<i class='bx bx-edit' ></i>"),
                ),
                css_class="mb-3",
                css_id="noteBox",
            ),
            ButtonHolder(
                Submit(
                    "Submit",
                    "Submit",
                ),
            ),
        )
