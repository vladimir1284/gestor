from django.forms import ModelForm
from django import forms
from ..models.lease import (
    Contract,
    HandWriting,
    Inspection,
    Tire
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText
from django.utils.safestring import mark_safe
from phonenumber_field.widgets import RegionalPhoneNumberWidget


class LeaseForm(ModelForm):
    class Meta:
        model = Contract
        fields = ('trailer_location', 'effective_date', 'payment_amount',
                  'security_deposit', 'payment_frequency', 'contract_term')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_phone'].widget = RegionalPhoneNumberWidget(
            region="US")
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
                        'client_id',
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
                'Emergency contact',
                HTML('<div id="id_trailer_conditions" class="col-12"></div>'),
                Div(
                    Div(
                        Field(
                            PrependedText('contact_name',
                                          mark_safe('<i class="bx bx-user"></i>'))
                        ),
                        css_class='col-md-6'
                    ),
                    Div(
                        Field(
                            PrependedText('contact_phone',
                                          mark_safe('<i class="bx bx-phone"></i>'))
                        ),
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


# class LeaseDocumentForm(ModelForm):
#     class Meta:
#         model = LeaseDocument
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


class TireUpdateForm(forms.ModelForm):
    class Meta:
        model = Tire
        fields = ['remaining_life']
