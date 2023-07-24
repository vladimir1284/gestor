from django.forms import ModelForm
from django import forms
from ..models.lease import (
    Lease,
    HandWriting,
    ContractDocument,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText


class LeaseForm(ModelForm):
    class Meta:
        model = Lease
        fields = ('location', 'location_file',
                  'effective_date', 'contract_end_date', 'number_of_payments',
                  'payment_amount', 'service_charge', 'security_deposit',
                  'inspection_date', 'current_condition')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['effective_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.fields['contract_end_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.fields['inspection_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Contract terms',
                Div(
                    Div(
                        Field('location', rows='2'),
                        css_class='col-md-6'
                    ),
                    Div(
                        'location_file',
                        css_class='col-md-6'
                    ),
                    css_class='row mb-3'
                ),
                Div(
                    Div(
                        'effective_date',
                        css_class='col-md-6'
                    ),
                    Div(
                        'contract_end_date',
                        css_class='col-md-6'
                    ),
                    css_class='row mb-3'
                ),
                Div(
                    Div(
                        'number_of_payments',
                        css_class='col-md-6'
                    ),
                    Div(
                        PrependedText('payment_amount', '$'),
                        css_class='col-md-6'
                    ),
                    css_class='row mb-3'
                ),
                Div(
                    Div(
                        PrependedText('service_charge', '$'),
                        css_class='col-md-6'
                    ),
                    Div(
                        PrependedText('security_deposit', '$'),
                        css_class='col-md-6'
                    ),
                    css_class='row mb-3'
                )
            ),
            Fieldset(
                'Inspection',
                HTML('<div id="id_trailer_conditions" class="col-12"></div>'),
                Div(
                    Div(
                        'current_condition',
                        css_class='col-md-6'
                    ),
                    Div(
                        'inspection_date',
                        css_class='col-md-6'
                    ),
                    css_class='row mb-3'
                ),
                ButtonHolder(
                    Submit('submit', 'Create contract',
                           css_class='btn btn-success')
                )
            )
        )


class HandWritingForm(ModelForm):
    class Meta:
        model = HandWriting
        fields = ('img', 'position', 'lease')

    img = forms.CharField(max_length=20000)


class ContractDocumentForm(ModelForm):
    class Meta:
        model = ContractDocument
        fields = ('lease', 'document')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'lease', 'document'
            ),
            ButtonHolder(
                Submit('submit', 'Add', css_class='btn btn-success')
            )
        )
