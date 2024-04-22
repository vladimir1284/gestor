from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from crispy_forms.layout import Layout

from services.models.towit_payment import TowitPayment
from utils.forms import BaseForm


class TowitPaymentForm(BaseForm):
    class Meta:
        model = TowitPayment
        fields = ("amount", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].label = "Towit Payment"
        self.fields["note"].label = "Reason"
        self.fields["note"].widget.attrs["rows"] = 2
        # if self.category.extra_charge > 0:
        #     self.fields["amount"].help_text = (
        #         f"Extra charge: {self.category.extra_charge}%"
        #     )

        self.helper.layout = Layout(
            Div(
                Div(PrependedText("amount", "$")),
            ),
            Div(
                Div(
                    PrependedText(
                        "note",
                        mark_safe("<i class='bx bx-note' ></i>"),
                    ),
                ),
            ),
        )
