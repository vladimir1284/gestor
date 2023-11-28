from .rental_model import RentalCost, RentalCostCategory
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
        model = RentalCostCategory
        fields = ('name', 'icon',)


class CommonLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                HTML(
                    """
                {% load static %}
                <img id="preview"
                alt="image"
                class="d-block rounded"
                height="100" width="100"
                {% if form.instance.image %}
                    src="{{ form.instance.image.url }}"
                {% else %}
                    src="{% static 'assets/img/icons/no_image.jpg' %}"
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
                Field('related_to', css_class="form-select"),
                css_class="mb-3"
            ),
            Div(
                Field('note', rows='2'),
                css_class="mb-3"
            )
        )


class CostsCreateForm(BaseForm):

    class Meta:
        model = RentalCost
        fields = (
            'image',
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

        # instance = kwargs.get('instance')
        # if instance is not None:
        #     self.fields['date'].help_text = instance.date.strftime('%b %d, %Y')

        self.helper.layout = Layout(
            CommonLayout(),
            Div(
                Field('date', css_class='form-control'),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )

        )


class CostsUpdateForm(BaseForm):

    class Meta:
        model = RentalCost
        fields = (
            'image',
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
            CommonLayout(),
            Div(
                Field('date', css_class='form-control'),  # Añade el campo 'date' al layout
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )
