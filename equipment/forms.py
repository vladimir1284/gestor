
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    Trailer,
    Vehicle,
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
)


class EquipmentTypeForm(forms.Form):
    CHOICES = [
        ('vehicle', _('Vehicle')),
        ('trailer', _('Trailer'))
    ]
    type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES,
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


class TrailerCreateForm(BaseForm):
    class Meta:
        model = Trailer
        fields = (
            'image',
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


class VehicleCreateForm(BaseForm):
    class Meta:
        model = Vehicle
        fields = (
            'image',
            'note',
            'vin',
            'year',
            'plate',
            'manufacturer',
            'model'
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
                Field('model',
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
