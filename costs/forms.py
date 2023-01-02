from .models import Cost, CostCategory
from django import forms
from utils.forms import CategoryCreateForm as BaseCategoryCreateForm
from utils.forms import (
    BaseForm,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.utils.translation import gettext_lazy as _


class CategoryCreateForm(BaseCategoryCreateForm):

    class Meta:
        model = CostCategory
        fields = ('name', 'icon',)


class CostsCreateForm(BaseForm):

    class Meta:
        model = Cost
        fields = (
            'file',
            'concept',
            'category',
            'amount',
            'related_to',
            'note',
            'date',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
        )
        self.helper.layout = Layout(
            Div(
                Field('file', css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Field('concept'),
                css_class="mb-3"
            ),
            Div(
                Field('category', css_class="form-select"),
                css_class="mb-3"
            ),
            Div(
                Field(
                    PrependedText('amount', '$')
                ),
                css_class="mb-3"
            ),
            Div(
                Field('date', css_class='form-control'),
                css_class="mb-3"
            ),
            Div(
                Field('related_to', css_class="form-select"),
                css_class="mb-3"
            ),
            Div(
                Field('note', rows='2'),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )

        )
