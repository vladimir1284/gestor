from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from django import forms
from django.template.loader import render_to_string

from rent.forms.lease import HTML
from rent.forms.lease import PrependedAppendedText
from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import Contract
from rent.models.lease import SecurityDepositDevolution


class DepositDiscountForm(forms.ModelForm):
    class Meta:
        model = DepositDiscount
        fields = [
            "duration",
            "location_towit",
            "location_note",
            "trailer_condition_discount",
        ]

    def __init__(
        self,
        *args,
        devolution: SecurityDepositDevolution | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        discount: DepositDiscount = self.instance

        duration = discount.expirate_in_days
        days = "day" if duration == 1 or duration == -1 else "days"
        sign = "before" if duration >= 0 else "after"
        css_class = (
            "danger" if duration < 0 else "success" if duration > 0 else "primary"
        )
        exp_date = discount.expiration_date.strftime("%b %d, %Y")

        self.fields["location_towit"] = forms.BooleanField(
            label="The trailer was returned at Towit Houston",
            required=False,
        )

        self.fields["location_note"].widget.attrs["rows"] = 3

        contract: Contract = self.instance.contract
        renovations = contract.renovation_ctx
        renovations["contract"] = contract
        renovations["renovations"] = [
            r
            for r in renovations["renovations"]
            if r.effective_date <= discount.expiration_date
        ]

        html_renovations = render_to_string(
            "rent/contract/discount/renovations_table.html",
            renovations,
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                # Duration
                Div(
                    Div(
                        HTML("<i class='bx bx-calendar' ></i>"),
                        css_class="input-group-addon",
                    ),
                    Div(
                        Div(
                            Field("duration"),
                            Div(
                                HTML(
                                    f""": <strong>{abs(duration)}</strong>
                                    {days}
                                    <strong class="text-{css_class}">{sign}</strong>
                                    <strong>{exp_date}</strong>.
                                    """,
                                ),
                            ),
                            css_class="flex",
                        ),
                        css_class="form-control",
                    ),
                    css_class="input-group",
                ),
                Div(
                    HTML(html_renovations),
                    css_class="mb-4 shadow-inner",
                ),
                # Location
                Div(
                    Div(
                        HTML("<i class='bx bx-map' ></i>"),
                        css_class="input-group-addon",
                    ),
                    Div(
                        Field("location_towit"),
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
                    css_id="location_note_box",
                ),
                # Debt dues
                Div(
                    HTML("Prepayments"),
                    css_class="",
                ),
                Div(
                    Div(
                        HTML("<i class='bx bx-dollar' ></i>"),
                        css_class="input-group-addon text-success",
                    ),
                    Div(
                        HTML(f"{self.instance.extra_payments}"),
                        css_class="form-control bg-mainBG",
                    ),
                    css_class="mb-3 input-group",
                ),
                # Debt dues
                Div(
                    HTML("Debts"),
                    css_class="",
                ),
                Div(
                    Div(
                        HTML("<i class='bx bx-dollar' ></i>"),
                        css_class="input-group-addon text-danger",
                    ),
                    Div(
                        HTML(f"{self.instance.debt}"),
                        css_class="form-control bg-mainBG",
                    ),
                    css_class="mb-3 input-group",
                ),
                # Tolls dues
                Div(
                    HTML("Tolls"),
                    css_class="",
                ),
                Div(
                    Div(
                        HTML("<i class='bx bx-dollar' ></i>"),
                        css_class="input-group-addon text-danger",
                    ),
                    Div(
                        HTML(f"{self.instance.tolls}"),
                        css_class="form-control bg-mainBG",
                    ),
                    css_class="mb-3 input-group",
                ),
                # Trailer condition discount
                Div(
                    PrependedText(
                        "trailer_condition_discount",
                        mark_safe("<i class='bx bx-dollar text-danger'></i>"),
                    ),
                    css_class="mb-3",
                ),
                css_class="mb-3",
            ),
            Div(
                css_id="totalDiscountBox",
            ),
            HTML(
                f"""
            <script>
            globalThis.DEBT = {self.instance.debt}
            globalThis.TOLLS = {self.instance.tolls}
            globalThis.EXTRA_PAY = {self.instance.extra_payments}
            </script>
            """
            ),
            # ButtonHolder(
            #     Submit(
            #         "submit",
            #         "Enviar",
            #         css_class="btn btn-success",
            #     ),
            # ),
        )
