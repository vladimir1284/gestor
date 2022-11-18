from django import forms
from .models import (
    Associated,
    Product,
    Unit,
    Order,
    Transaction,
    StoreLocations,
    ProductCategory,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _


class AssociatedCreateForm(forms.ModelForm):

    class Meta:
        model = Associated
        fields = (
            'name',
            'company',
            'address',
            'note',
            'email',
            'avatar',
            'phone_number',
            'type'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break

        self.fields['address'].widget.attrs = {'rows': 2}

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText('name',
                                  '<i class="bx bx-user-circle"></i>')
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('type',
                                  '<i class="bx bx-certification"></i>',
                                  css_class="form-select")
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('phone_number',
                                  '<i class="bx bx-phone"></i>')
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedAppendedText('email',
                                          '<i class="bx bx-envelope"></i>',
                                          '@ejemplo.com')
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('company',
                                  '<i class="bx bx-buildings"></i>'),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('address',
                                  '<i class="bx bx-building-house"></i>'),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('note', rows='2')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('avatar')
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            'type',
            'concept',
            'note',
            'associated'
        )

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
        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText('associated',
                                      '<i class="bx bx-user-circle"></i>',
                                      css_class="form-select")
                    ),
                    css_class="col-10"
                ),
                Div(
                    HTML(
                        """
                    <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                       type="button"
                       href="{% url 'create-associated' %}">
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
                Field(
                    PrependedText('type',
                                  '<i class="bx bx-certification"></i>',
                                  css_class="form-select")
                ),
                css_class="row mb-3"
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


class CommonTransactionLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Div(
                    Field(
                        PrependedText('price', '$')
                    ),
                    css_class="col-6"
                ),
                Div(
                    Div(
                        AppendedText('tax', '%')
                    ),
                    css_class="col-6"
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('quantity'
                          ),
                    css_class="col-4"
                ),
                Div(
                    Div(
                        Field('unit',
                              css_class="form-select")
                    ),
                    css_class="col-8"
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('note', rows='2')
                ),
                css_class="mb-3"
            )
        )


class TransactionCreateForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'price',
            'note',
            'quantity',
            'unit',
            'tax'
        )

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
        self.helper.add_input(Submit("submit", "Save"))
        self.helper.layout = Layout(CommonTransactionLayout())


class TransactionProviderCreateForm(TransactionCreateForm):
    associated = forms.fields_for_model(Order)['associated']

    class Meta:
        model = Transaction
        fields = (
            'price',
            'note',
            'quantity',
            'unit',
            'tax',
            'associated'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            CommonTransactionLayout(),
            Div(
                Field('associated',
                      css_class="form-select")
            )
        )


class CategoryCreateForm(forms.ModelForm):

    class Meta:
        model = ProductCategory
        fields = ('name', 'icon',)

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


class UnitCreateForm(forms.ModelForm):

    class Meta:
        model = Unit
        fields = ('name',
                  'factor',
                  'magnitude')

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
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('name')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('factor')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('magnitude')
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class ProductCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('name',
                  'description',
                  'unit',
                  'category',
                  'type',
                  'sell_tax',
                  'suggested_price',
                  'max_price',
                  'quantity_min')

    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            kwargs.pop('title')
        else:
            self.title = _("Create Product")

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
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        self.title,
                        Div(
                            Div(
                                Field('name')
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('description', rows='2')
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('unit', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('category', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field('type', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        css_class="card-body"
                    ),
                    css_class="card mb-4"
                ),
                css_class="col-xxl"
            ),

            Div(
                Div(
                    Fieldset(
                        _("Advance configuration"),
                        Div(
                            Div(
                                Field('quantity_min', css_class="form-select")
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    AppendedText('suggested_price', '%')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    AppendedText('max_price', '%')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        Div(
                            Div(
                                Field(
                                    AppendedText('sell_tax', '%')
                                )
                            ),
                            css_class="mb-3"
                        ),
                        ButtonHolder(
                            Submit('submit', 'Enviar',
                                   css_class='btn btn-success')
                        ),
                        css_class="card-body"
                    ),
                    css_class="card mb-4"
                ),
                css_class="col-xxl"
            )
        )
