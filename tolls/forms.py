from django import forms
from utils.forms import (
    BaseForm,
)
from .models import TollDue
from rent.models.lease import Contract
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText


class TollCreateForm(BaseForm):

    class Meta:
        model = TollDue
        fields = (
            'amount',
            'created_date',
            'stage',
            'invoice_number',
            'invoice',
            'plate',
            'contract'
        )

    def __init__(self, *args, **kwargs):
        self.plate = kwargs.pop('plate', None)
        self.contract = kwargs.pop('contract', None)
        super().__init__(*args, **kwargs)
        self.fields['created_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )

        if self.plate:
            self.fields['plate'].initial = self.plate
        if self.contract:
            self.fields['contract'].initial = self.contract

        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText('amount', '$')
                ),
                css_class="mb-3"
            ),
            Div(
                Field('created_date', css_class='form-control'),
                css_class="mb-3"
            ),
            Div(
                Field('stage', css_class="form-select"),
                css_class="mb-3"
            ),
            Div(
                Field('invoice_number'),
                css_class="mb-3"
            ),
            Div(
                Field('invoice'),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            ),
            Field('plate', type='hidden', value=self.plate.id or ''),
            Field('contract', type='hidden', value=self.contract.id or '')

        )


class TollUpdateForm(BaseForm):

    class Meta:
        model = TollDue
        fields = (
            'amount',
            'created_date',
            'stage',
            'invoice_number',
            'invoice',
            'plate',
            'contract'
        )

    def __init__(self, *args, **kwargs):
        self.plate = kwargs.pop('plate', None)
        super().__init__(*args, **kwargs)
        self.fields['created_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )

        if self.plate:
            self.fields['contract'].queryset = Contract.objects.filter(
                trailer=self.plate.trailer)
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText('amount', '$')
                ),
                css_class="mb-3"
            ),
            Div(
                Field('created_date', css_class='form-control'),
                css_class="mb-3"
            ),
            Div(
                Field('stage', css_class="form-select"),
                css_class="mb-3"
            ),
            Div(
                Field('invoice_number'),
                css_class="mb-3"
            ),
            Div(
                Field('invoice'),
                css_class="mb-3"
            ),
            Div(
                Field('plate', disabled=True, value=self.plate.id),
                css_class="mb-3"
            ),
            Div(
                Field('contract'),
                css_class="mb-3"
            ),

            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            ),
            Field('plate', type='hidden', value=self.plate.id),
        )
