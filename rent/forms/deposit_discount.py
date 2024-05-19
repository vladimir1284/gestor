from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from django import forms

from rent.forms.lease import HTML
from rent.models.deposit_discount import DepositDiscount


class DepositDiscountForm(forms.ModelForm):
    class Meta:
        model = DepositDiscount
        fields = [
            "location_towit",
            "location_note",
            "discount_trailer_cond",
            "due",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        duration = self.instance.duration
        days = "day" if duration == 1 or duration == -1 else "days"
        sign = "before" if duration < 0 else "after"
        css_class = (
            "danger" if duration < 0 else "success" if duration > 0 else "primary"
        )

        self.fields["location_towit"] = forms.BooleanField(
            label="The trailer was returned at Towit Houston",
            required=False,
            # help_text="Was the trailer returned at Towit Houston?",
        )

        self.fields["location_note"].widget.attrs["rows"] = 3

        self.fields["discount_trailer_cond"].label = "Trailer condition discount"
        self.fields["discount_trailer_cond"].required = True

        self.fields["due"].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(
                        f"""
                        Duration:
                        The trailer was returned
                        <strong>{abs(duration)}</strong>
                        {days}
                        <strong class="text-{css_class}">{sign}</strong>
                        .
                        """,
                    ),
                    css_class="mb-3",
                ),
                Div(
                    Div(
                        HTML("<i class='bx bx-map' ></i>"),
                        css_class="input-group-addon",
                    ),
                    Div(
                        # HTML("Returned location"),
                        Field("location_towit"),
                        # PrependedText(
                        #     "location_towit",
                        #     mark_safe("<i class='bx bx-map' ></i>"),
                        # ),
                        css_class="form-control",
                    ),
                    css_class="mb-2 input-group",
                ),
                Div(
                    PrependedText(
                        "location_note",
                        mark_safe("<i class='bx bx-edit' ></i>"),
                    ),
                    css_class="mb-4",
                ),
                Div(
                    PrependedText(
                        "discount_trailer_cond",
                        mark_safe("<i class='bx bxs-car-mechanic'></i>"),
                    ),
                    css_class="mb-3",
                ),
                Div(
                    PrependedText(
                        "due",
                        mark_safe("<i class='bx bx-dollar' ></i>"),
                    ),
                    css_class="mb-3",
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
