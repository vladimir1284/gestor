from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.template.defaultfilters import default
from django.utils.timezone import datetime
from django.utils.timezone import make_aware
from django.utils.translation.trans_real import mark_safe

from rent.models.lease import SecurityDepositDevolution
from rent.models.trailer_deposit import TrailerDeposit
from rent.models.trailer_deposit import TrailerDepositTrace
from rent.tools.get_conditions import get_on_hold_reasons


class TrailerDepositForm(forms.ModelForm):
    class Meta:
        model = TrailerDeposit
        fields = ("date", "days", "amount", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial["date"] = datetime.now()
        self.fields["date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
            label="Initial date",
        )

        self.fields["note"].widget.attrs["rows"] = 3
        self.fields["days"].label = "Validity days"

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText(
                            "amount",
                            mark_safe("<i class='bx bx-money' ></i>"),
                        ),
                    ),
                ),
                css_class="mb-3",
            ),
            Div(
                Div(
                    Field(
                        PrependedText(
                            "date",
                            mark_safe(
                                "<i class='bx bx-calendar-event'></i>",
                            ),
                        ),
                    ),
                ),
                css_class="mb-3",
            ),
            Div(
                Div(
                    Field(
                        PrependedText(
                            "days",
                            mark_safe(
                                "<i class='bx bx-calendar' ></i>",
                            ),
                        ),
                    ),
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

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date.date() < datetime.now().date():
            raise forms.ValidationError("Insert a valid date")
        return date


class TrailerDepositRenovationForm(forms.ModelForm):
    class Meta:
        model = TrailerDepositTrace
        fields = ("days", "amount", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["note"].widget.attrs["rows"] = 3

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText(
                            "amount",
                            mark_safe("<i class='bx bx-money' ></i>"),
                        ),
                    ),
                ),
                css_class="mb-3",
            ),
            Div(
                Div(
                    Field(
                        PrependedText(
                            "days",
                            mark_safe(
                                "<i class='bx bx-calendar' ></i>",
                            ),
                        ),
                    ),
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


class OnHoldDepositDevolutionForm(forms.ModelForm):
    class Meta:
        model = SecurityDepositDevolution
        fields = ["amount", "reason", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)

        if instance:
            self.fields["amount"].initial = instance.total_deposited_amount

        self.fields["amount"].widget.attrs["x-model"] = "retAmount"
        self.fields["amount"].widget.attrs["x-ref"] = "retAmountField"
        self.fields["amount"].label = "Amount to return"

        reasons = get_on_hold_reasons()
        print(reasons)
        self.fields["reason"] = forms.ChoiceField(
            choices=reasons,
        )

        self.fields["note"].widget.attrs["rows"] = "3"

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            PrependedText("amount", mark_safe("<i class='bx bx-dollar'></i>")),
            PrependedText("reason", mark_safe("<i class='bx bx-info-circle' ></i>")),
            PrependedText("note", mark_safe("<i class='bx bx-edit' ></i>")),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )
