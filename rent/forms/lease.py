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


class LeaseForm(ModelForm):
    class Meta:
        model = Contract
        fields = ('trailer_location', 'effective_date', 'payment_amount',
                  'security_deposit', 'payment_frequency', 'contract_term',
                  'service_charge')

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
            PrependedText('security_deposit', '$'),
            'payment_frequency',
            AppendedText('contract_term', 'weeks'),
            PrependedText('payment_amount', '$'),
            PrependedText('service_charge', '$'),
            ButtonHolder(
                Submit('submit', 'Create contract',
                       css_class='btn btn-success')
            )
        )


class HandWritingForm(ModelForm):
    class Meta:
        model = HandWriting
        fields = ('img', 'position', 'lease')

    img = forms.CharField(max_length=20000)


# class ContractDocumentForm(ModelForm):
#     class Meta:
#         model = ContractDocument
#         fields = ('lease', 'document')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Fieldset(
#                 '',
#                 'lease', 'document'
#             ),
#             ButtonHolder(
#                 Submit('submit', 'Add', css_class='btn btn-success')
#             )
#         )


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
                  'license_number', 'license_file',
                  'client_id', 'client_address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'mb-3'
        self.helper.layout = Layout(
            Fieldset('Documents',
                     'insurance_number',
                     'insurance_file',
                     'license_number',
                     'license_file',
                     'client_id',
                     Field('client_address', rows='2')
                     ),
            Fieldset('Emergency Contact',
                     'contact_name',
                     'contact_phone'
                     ),
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

        self.helper.layout = Layout(
            CommonContactLayout(),
            Field('type'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )
