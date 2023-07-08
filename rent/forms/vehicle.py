
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.bootstrap import PrependedText
from django.utils import timezone

from rent.models.vehicle import (
    Trailer,
    Manufacturer,
    TrailerPicture,
    TrailerDocument,
)
from utils.forms import (
    BaseForm,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    ButtonHolder,
    Submit,
    Div,
    Field,
    Fieldset,
)


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ('brand_name', 'url', 'icon')

    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('brand_name')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('url')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('icon', css_class="form-select")
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class TrailerCreateForm(BaseForm):
    class Meta:
        model = Trailer
        fields = (
            'note',
            'vin',
            'year',
            'cdl',
            'type',
            'plate',
            'manufacturer',
            'axis_number',
            'load'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Div(
                Field('manufacturer',
                      css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Field('type',
                      css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Field('year',
                      css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Field('vin'),
                css_class="row mb-3"
            ),
            Div(
                Field('plate'),
                css_class="row mb-3"
            ),
            Div(
                Field('cdl'),
                css_class="row mb-3"
            ),
            Div(
                Field('axis_number',
                      css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Field('load',
                      css_class="form-select"),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('note', rows='2')
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar',
                       css_class='btn btn-success')
            )
        )


class TrailerPictureForm(forms.ModelForm):
    class Meta:
        model = TrailerPicture
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('image'),
                css_class="row mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class CommonDocumentLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(Fieldset(
            'Document Information',
            Div(
                Field('name', placeholder='Name'),
                css_class='mb-3'
            ),
            Div(
                Field('file', placeholder='Name'),
                css_class='mb-3'
            ),
            Div(
                Field('note', placeholder='Note', rows='2'),
                css_class='mb-3'
            ),
            Div(
                Field('is_active'),
                css_class='mb-3'
            ),
            css_class='row mb-3'
        )
        )


class TrailerDocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = TrailerDocument
        fields = ('name', 'note', 'file', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            CommonDocumentLayout(),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class TrailerDocumentForm(forms.ModelForm):
    class Meta:
        model = TrailerDocument
        fields = ('name', 'note', 'file',
                  'expiration_date', 'remainder_days', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expiration_date'] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={'type': 'date'},
            ),
            required=False
        )
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            CommonDocumentLayout(),
            Div(
                Field('expiration_date'),
                css_class="mb-3"
            ),
            Div(
                Field('remainder_days', placeholder='Remainder days'),
                css_class='mb-3'
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        expiration_date = cleaned_data.get('expiration_date')
        remainder_days = cleaned_data.get('remainder_days')
        if remainder_days and expiration_date:
            remainder_date = expiration_date - \
                timezone.timedelta(days=remainder_days)
            if remainder_date < timezone.now():
                raise forms.ValidationError(
                    'Reminder date cannot be in the past.')
        return cleaned_data
