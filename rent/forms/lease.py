from django.forms import ModelForm
from django import forms
from phonenumber_field.widgets import RegionalPhoneNumberWidget
from phonenumber_field.modelfields import PhoneNumberField
from ..models.lease import (
    Contract,
    HandWriting,
    Inspection,
    Tire,
    LesseeData,
    Payment,
    Lease,
    LeaseDocument,
    LeaseDeposit,
    Due,
    SecurityDepositDevolution,
)
from django.forms import modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText
from django.utils.safestring import mark_safe
from phonenumber_field.widgets import RegionalPhoneNumberWidget
from users.forms import BaseContactForm, CommonContactLayout
from django.forms import HiddenInput
from users.models import Associated


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = ('trailer_location', 'effective_date', 'payment_amount',
                  'security_deposit', 'payment_frequency', 'contract_term',
                  'service_charge', 'contract_type', 'total_amount')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['effective_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Field('trailer_location', rows='2'),
            'effective_date',
            PrependedText('payment_amount', '$'),
            'payment_frequency',
            AppendedText('contract_term', 'months'),
            PrependedText('service_charge', '$'),
            PrependedText('security_deposit', '$'),
            Field('contract_type'),
            PrependedText('total_amount', '$'),
            ButtonHolder(
                Submit('submit', 'Create contract',
                       css_class='btn btn-success')
            )
        )


class HandWritingForm(ModelForm):
    class Meta:
        model = HandWriting
        fields = ('img',)  # 'position', 'lease')

    img = forms.CharField(max_length=2000000)


class InspectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            'inspection_date',
            'number_of_main_tires',
            'number_of_spare_tires',
            Field('note', rows='2'),
            Fieldset(
                'Accessories',
                'winche',
                'megaramp',
                'ramp',
                'ramp_material',
                'ancillary_battery',
                'strap_4inch',
            ),
            Submit('submit', 'Enviar')
        )

    class Meta:
        model = Inspection
        fields = ('inspection_date',
                  'number_of_main_tires',
                  'number_of_spare_tires',
                  'winche',
                  'megaramp',
                  'ramp',
                  'ramp_material',
                  'note',
                  'ancillary_battery',
                  'strap_4inch')


TireFormSet = modelformset_factory(
    Tire, fields=('remaining_life',), edit_only=True)


class LesseeDataForm(forms.ModelForm):
    class Meta:
        model = LesseeData
        fields = ('contact_name', 'contact_phone',
                  'insurance_number', 'insurance_file',
                  'license_number', 'license_file', 'client_address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Fieldset('Documents',
                     'license_number',
                     'license_file',
                     Field('client_address', rows='2'),
                     'insurance_number',
                     'insurance_file'
                     ),
            Fieldset('Emergency Contact',
                     'contact_name',
                     'contact_phone'
                     ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )

class SecurityDepositDevolutionForm(forms.ModelForm):
    class Meta:
        model = SecurityDepositDevolution
        fields = ('amount', 'returned')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)

        if instance:
            self.fields['amount'].initial = instance.contract.security_deposit

        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            PrependedText('amount', '$'),
            Field('returned'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class AssociatedCreateForm(BaseContactForm):

    class Meta(BaseContactForm.Meta):
        model = Associated
        fields = BaseContactForm.Meta.fields + ['type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['type'].widget = HiddenInput()
        self.fields['phone_number'].required = True
        self.fields['email'].required = True

        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            CommonContactLayout(),
            Field('type'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date_of_payment', 'amount', 'lease', 'sender_name']

    def __init__(self, *args, **kwargs):
        if 'client' in kwargs:
            client = kwargs['client']
            kwargs.pop('client')
        super().__init__(*args, **kwargs)
        self.fields['lease'].queryset = Lease.objects.filter(
            contract__lessee=client, contract__stage="active")
        self.fields['date_of_payment'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        # Get the last not null sender_name for other instances of Payment with the same lease
        if client:
            last_sender_name = Payment.objects.filter(
                client=client).exclude(sender_name__isnull=True).last()
            if last_sender_name:
                self.fields['sender_name'].initial = last_sender_name.sender_name

        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Field('lease'),
            Field('sender_name'),
            Field('date_of_payment'),
            Field('amount'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class LeaseUpdateForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ('payment_amount', 'payment_frequency')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['payment_amount'].initial = instance.payment_amount
            self.fields['payment_frequency'].initial = instance.payment_frequency

        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            PrependedText('payment_amount', '$'),
            Field('payment_frequency'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class LeaseDocumentForm(forms.ModelForm):
    class Meta:
        model = LeaseDocument
        fields = ('name', 'note', 'file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name', placeholder='Name'),
            Field('file', placeholder='Name'),
            Field('note', placeholder='Note', rows='2'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class DueForm(forms.ModelForm):
    class Meta:
        model = Due
        fields = ('amount', 'note')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            PrependedText('amount', '$'),
            Field('note', placeholder='Note', rows='2'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class LeaseDepositForm(forms.ModelForm):
    class Meta:
        model = LeaseDeposit
        fields = ('amount', 'date', 'note')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            PrependedText('amount', '$'),
            Field('date'),
            Field('note', placeholder='Note', rows='2'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )
