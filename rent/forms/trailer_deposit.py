from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms

from rent.models.trailer_deposit import TrailerDeposit


class TrailerDepositForm(forms.ModelForm):
    class Meta:
        model = TrailerDeposit
        fields = ("date", "amount", "note")

    def __init__(self, *args, **kwargs):
        super(TrailerDepositForm, self).__init__(*args, **kwargs)
        self.fields["date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Field("amount"),
                ),
                css_class="mb-3",
            ),
            Div(
                Div(
                    Field("date"),
                ),
                css_class="mb-3",
            ),
            Div(
                Div(
                    Field("note"),
                ),
                css_class="mb-3",
            ),
            ButtonHolder(
                Submit(
                    "submit",
                    "Enviar",
                    css_class="btn btn-success",
                ),
            ),
        )
