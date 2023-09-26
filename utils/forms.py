from django import forms
from django.utils.safestring import mark_safe

from .models import (
    Category,
    Order,
    Plate,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.utils.translation import gettext_lazy as _


class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'


class PlateForm(forms.ModelForm):
    class Meta:
        model = Plate
        fields = ['plate', 'reason', 'note', 'driver_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            Field('driver_name'),
            Field('plate', label="Plate/VIN"),
            Field('reason'),
            Field('note', rows='2'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )

        )


class CategoryCreateForm(BaseForm):

    class Meta:
        fields = ('name', 'icon',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('name')
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


class OrderCreateForm(BaseForm):

    class Meta:
        model = Order
        fields = (
            'concept',
            'note',
            'associated',
            'position',
        )

    href = "{% url 'create-provider' %}?next={{ request.path|urlencode }}"
    tooltip = "Modify provider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText('associated',
                                      mark_safe(
                                          '<i class="bx bx-user-circle"></i>'),
                                      css_class="form-select")
                    ),
                    css_class="col-10"
                ),
                Div(
                    HTML(
                        F"""
                    <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                       type="button"
                       href="{self.href}"
                       data-bs-toggle="tooltip"
                       data-bs-offset="0,4"
                       data-bs-placement="left"
                       data-bs-html="true"
                       title=""
                       data-bs-original-title="<span>{self.tooltip}</span>">
                        <span class="tf-icons bx bx-plus"></span>
                    </a>
                    """),
                    css_class="col-2 position-relative"
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('concept')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('position')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('note', rows='2')
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )
