from datetime import datetime

from crispy_forms.bootstrap import AppendedText
from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from dateutil.relativedelta import relativedelta
from django import forms
from django.forms import HiddenInput
from django.forms import ModelForm
from django.forms import modelformset_factory
from django.urls import reverse
from django.utils import timezone
from twilio.rest.pricing.v1 import phone_number

from ..models.lease import Contract
from ..models.lease import Due
from ..models.lease import Inspection
from ..models.lease import Lease
from ..models.lease import LeaseDeposit
from ..models.lease import LeaseDocument
from ..models.lease import LesseeData
from ..models.lease import Note
from ..models.lease import Payment
from ..models.lease import SecurityDepositDevolution
from ..models.lease import Tire
from rent.tools.get_conditions import get_rent_conditions_template
from template_admin.models.template_version import TemplateVersion
from users.forms import BaseContactForm
from users.forms import CommonContactLayout
from users.models import Associated


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = (
            "trailer_location",
            "effective_date",
            "payment_amount",
            "security_deposit",
            "payment_frequency",
            "contract_term",
            "renovation_term",
            "service_charge",
            "contract_type",
            "total_amount",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["effective_date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
        )

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            PrependedText(
                "trailer_location",
                mark_safe("<i class='bx bx-current-location'></i>"),
                rows="2",
            ),
            PrependedText(
                "effective_date",
                mark_safe("<i class='bx bx-calendar-event' ></i>"),
            ),
            PrependedText(
                "payment_amount",
                mark_safe("<i class='bx bx-dollar' ></i>"),
            ),
            PrependedText(
                "payment_frequency",
                mark_safe("<i class='bx bx-calendar-plus' ></i>"),
            ),
            PrependedAppendedText(
                "contract_term",
                mark_safe("<i class='bx bx-calendar-exclamation' ></i>"),
                "months",
            ),
            PrependedAppendedText(
                "renovation_term",
                mark_safe("<i class='bx bx-calendar-check' ></i>"),
                "months",
            ),
            PrependedText(
                "service_charge",
                mark_safe("<i class='bx bx-dollar' ></i>"),
            ),
            PrependedText(
                "security_deposit",
                mark_safe("<i class='bx bx-dollar' ></i>"),
            ),
            PrependedText(
                "contract_type",
                mark_safe("<i class='bx bx-file' ></i>"),
            ),
            PrependedText(
                "total_amount",
                mark_safe("<i class='bx bx-dollar' ></i>"),
            ),
            ButtonHolder(
                Submit("submit", "Create contract", css_class="btn btn-success")
            ),
        )

    def clean_payment_amount(self):
        pay = self.cleaned_data["payment_amount"]
        if pay > 0:
            return pay
        raise forms.ValidationError("Payment amount must be greater than zero")


class InspectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inspection_date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
        )
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            "inspection_date",
            "number_of_main_tires",
            "number_of_spare_tires",
            Field("note", rows="2"),
            Fieldset(
                "Accessories",
                "winche",
                "megaramp",
                "ramp",
                "ramp_material",
                "ancillary_battery",
                "strap_4inch",
            ),
            Submit("submit", "Enviar"),
        )

    class Meta:
        model = Inspection
        fields = (
            "inspection_date",
            "number_of_main_tires",
            "number_of_spare_tires",
            "winche",
            "megaramp",
            "ramp",
            "ramp_material",
            "note",
            "ancillary_battery",
            "strap_4inch",
        )


TireFormSet = modelformset_factory(Tire, fields=("remaining_life",), edit_only=True)


class LesseeDataForm(forms.ModelForm):
    class Meta:
        model = LesseeData
        fields = (
            "insurance_number",
            "insurance_file",
            "license_number",
            "license_file",
            "client_address",
            "contact_name",
            "contact_phone",
            "contact_file",
            "contact2_name",
            "contact2_phone",
            "contact2_file",
            "contact3_name",
            "contact3_phone",
            "contact3_file",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            Fieldset(
                "Documents",
                "license_number",
                "license_file",
                Field("client_address", rows="2"),
                "insurance_number",
                "insurance_file",
            ),
            Div(
                Fieldset(
                    "Emergency Contact (Required)",
                    "contact_name",
                    "contact_phone",
                    "contact_file",
                ),
                Fieldset(
                    "Emergency Contact 2 (Optional)",
                    "contact2_name",
                    "contact2_phone",
                    "contact2_file",
                ),
                Fieldset(
                    "Emergency Contact 3 (Optional)",
                    "contact3_name",
                    "contact3_phone",
                    "contact3_file",
                ),
                css_class="xl:flex gap-2",
            ),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class SecurityDepositDevolutionForm(forms.ModelForm):
    class Meta:
        model = SecurityDepositDevolution
        fields = ("refund_date", "note", "immediate_refund")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["immediate_refund"].required = False

        self.initial["refund_date"] = datetime.now().date() + relativedelta(months=1)
        self.fields["refund_date"] = forms.DateField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
            required=False,
        )

        self.fields["note"].required = False
        self.fields["note"].label = "Note*"
        self.fields["note"].widget.attrs["rows"] = 3

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field("immediate_refund"),
                css_class="mb-2",
            ),
            Div(
                PrependedText(
                    "refund_date",
                    mark_safe("<i class='bx bx-calendar'></i>"),
                ),
                css_id="refundDateBox",
            ),
            Div(
                PrependedText(
                    "note",
                    mark_safe("<i class='bx bx-edit' ></i>"),
                ),
                css_id="refundNoteBox",
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data["refund_date"]
        immediate = cleaned_data["immediate_refund"]
        print(immediate, date)

        if not immediate:
            if date is None or date == "":
                raise forms.ValidationError("Please insert a refund date")
            if date < datetime.now().date():
                raise forms.ValidationError("Please insert a valid refund date")

        return cleaned_data


class AssociatedCreateForm(BaseContactForm):
    has_guarantor = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "x-model": "has_guarantor",
                "x-ref": "guarantor",
            }
        ),
    )

    class Meta(BaseContactForm.Meta):
        model = Associated
        fields = BaseContactForm.Meta.fields + ["type"]

    def __init__(
        self,
        *args,
        use_client_url: dict | None = None,
        ask_guarantor: bool = False,
        **kwargs,
    ):
        self.use_client_url = use_client_url
        self.buttons = ButtonHolder(
            Submit("submit", "Enviar", css_class="btn btn-success")
        )

        super().__init__(*args, **kwargs)

        self.fields["type"].widget = HiddenInput()
        self.fields["phone_number"].required = True
        self.fields["email"].required = True

        self.helper.field_class = "mb-3"

        self.helper.layout = Layout(
            CommonContactLayout(),
            Field("type"),
            Field("has_guarantor") if ask_guarantor else HTML(""),
            self.buttons,
        )

    def validate_client(self):
        if self.use_client_url is None or "url" not in self.use_client_url:
            return
        if "phone_number" not in self.cleaned_data:
            return

        phone = self.cleaned_data["phone_number"]
        client = Associated.objects.filter(phone_number=phone).last()
        if client is None:
            return

        url_name = self.use_client_url["url"]
        args: list = []
        if "args" in self.use_client_url:
            args: list = self.use_client_url["args"]
            try:
                idx = args.index("{client_id}")
                args[idx] = client.id
            except Exception:
                pass

        url = reverse(url_name, args=args)
        self.buttons.append(
            HTML(
                f"""<a class='btn btn-outline-primary' href='{url}'>
                Use client
                <strong>{client.name}</strong>
                with phone number
                <strong>{client.phone_number}</strong>
                </a>"""
            )
        )

    def clean(self):
        self.validate_client()
        return super().clean()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["date_of_payment", "amount", "lease", "sender_name"]

    def __init__(self, *args, **kwargs):
        if "client" in kwargs:
            client = kwargs["client"]
            kwargs.pop("client")
        super().__init__(*args, **kwargs)
        self.fields["lease"].queryset = Lease.objects.filter(
            contract__lessee=client, contract__stage="active"
        )
        self.fields["date_of_payment"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
        )
        # Get the last not null sender_name for other instances of Payment with the same lease
        if client:
            last_sender_name = (
                Payment.objects.filter(client=client)
                .exclude(sender_name__isnull=True)
                .last()
            )
            if last_sender_name:
                self.fields["sender_name"].initial = last_sender_name.sender_name

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            Field("lease"),
            Field("sender_name"),
            Field("date_of_payment"),
            Field("amount"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class LeaseUpdateForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ("payment_amount", "payment_frequency")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.fields["payment_amount"].initial = instance.payment_amount
            self.fields["payment_frequency"].initial = instance.payment_frequency

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            PrependedText("payment_amount", "$"),
            Field("payment_frequency"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("text", "has_reminder", "reminder_date", "file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["reminder_date"] = forms.DateTimeField(
            widget=forms.DateInput(attrs={"type": "date"}), required=False
        )

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("text", placeholder="Note...", rows="2"),
            Field("file", placeholder="Attachment"),
            Field("has_reminder", css_class="mb-3"),
            Field("reminder_date"),
            ButtonHolder(Submit("submit", "Add", css_class="btn btn-success")),
        )

    def clean(self):
        cleaned_data = super().clean()
        reminder_date = cleaned_data.get("reminder_date")
        has_reminder = cleaned_data.get("has_reminder")
        if has_reminder:
            if reminder_date:
                if reminder_date < timezone.now():
                    raise forms.ValidationError("Reminder date cannot be in the past!")
            else:
                raise forms.ValidationError(
                    "If the reminder checkbox is selected you must provide a remidner date!"
                )
        return cleaned_data


class LeaseDocumentForm(forms.ModelForm):
    class Meta:
        model = LeaseDocument
        fields = ("name", "note", "file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("name", placeholder="Name"),
            Field("file", placeholder="Name"),
            Field("note", placeholder="Note", rows="2"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class DueForm(forms.ModelForm):
    class Meta:
        model = Due
        fields = ("amount", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            PrependedText("amount", "$"),
            Field("note", placeholder="Note", rows="2"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class LeaseDepositForm(forms.ModelForm):
    class Meta:
        model = LeaseDeposit
        fields = ("amount", "date", "note")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
        )
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            PrependedText("amount", "$"),
            Field("date"),
            Field("note", placeholder="Note", rows="2"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )
