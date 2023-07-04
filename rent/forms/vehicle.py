
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
    HTML,
    Field,
    Fieldset,
)


class PictureLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                HTML(
                    """
                {% load static %}
                <img id="preview"
                alt="vehicle picture"
                class="d-block rounded"
                height="100" width="100"
                {% if form.image %}
                    src="/media/{{ form.image.value }}"
                {% else %}
                    src="{% static 'images/icons/no_image.jpg' %}"
                {% endif %}>
                """
                ),
                css_class="d-flex align-items-start align-items-sm-center gap-4"
            ),
            Div(
                Div(
                    Field('image')
                ),
                css_class="mb-3"
            )
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
            HTML(
                """
                <img id="preview" 
                {% if form.icon.value %}
                    class="img-responsive" 
                    src="/media/{{ form.icon.value }}"
                {% endif %}">
                """
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
            PictureLayout(),
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


class TrailerDocumentForm(forms.ModelForm):
    class Meta:
        model = TrailerDocument
        fields = ('name', 'note', 'document_type',
                  'expiration_date', 'remainder_days', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Document Information',
                Div(
                    Field('name', placeholder='Name'),
                    css_class='col-md-6'
                ),
                Div(
                    Field('note', placeholder='Note'),
                    css_class='col-md-6'
                ),
                Div(
                    Field('document_type', placeholder='Document type'),
                    css_class='col-md-6'
                ),
                Div(
                    PrependedText('expiration_date', '<i class="fa fa-calendar"></i>',
                                  placeholder='Expiration date', autocomplete='off'),
                    css_class='col-md-6'
                ),
                Div(
                    Field('remainder_days', placeholder='Remainder days'),
                    css_class='col-md-6'
                ),
                Div(
                    Field('is_active'),
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            Div(
                HTML('<hr>'),
                Field('trailer', type='hidden'),
                HTML('{% crispy form %}'),
            ),
            HTML('{% crispy form.helper %}'),
        )

    def clean(self):
        cleaned_data = super().clean()
        expiration_date = cleaned_data.get('expiration_date')
        remainder_days = cleaned_data.get('remainder_days')
        if remainder_days and expiration_date:
            remainder_date = expiration_date - \
                timezone.timedelta(days=remainder_days)
            if remainder_date < timezone.now().date():
                raise forms.ValidationError(
                    'Reminder date cannot be in the past.')
        return cleaned_data
