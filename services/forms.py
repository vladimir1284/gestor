from django import forms
from utils.models import (
    Order,
)
from .models import (
    Service,
    ServiceTransaction,
    ServiceCategory,
    Expense,
)
from utils.forms import (
    BaseForm,
    CategoryCreateForm as BaseCategoryCreateForm,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    ButtonHolder,
    Submit,
    Div,
    HTML,
    Field,
)
from crispy_forms.bootstrap import (
    PrependedText,
    AppendedText,
    PrependedAppendedText,
)
from django.utils.translation import gettext_lazy as _


class OrderCreateForm(BaseForm):
    class Meta:
        model = Order
        fields = (
            'concept',
            'note',
            'badge'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('concept')
                ),
                css_class="mb-3"
            ),
            Div(
                Div(
                    Field('badge')
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


class CategoryCreateForm(BaseCategoryCreateForm):

    class Meta:
        model = ServiceCategory
        fields = ('name', 'icon',)


class CommonTransactionLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Div(
                    Field(
                        PrependedText('price', '$')
                    ),
                    css_class="col-md-4 mb-3"
                ),
                Div(
                    Div(
                        AppendedText('tax', '%')
                    ),
                    css_class="col-md-4 mb-3"
                ),
                Div(
                    Field('quantity'),
                    css_class="col-md-4 mb-3"
                ),
                css_class="row"
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
        model = ServiceTransaction
        fields = (
            'price',
            'note',
            'quantity',
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
        model = ServiceTransaction
        fields = (
            'price',
            'note',
            'quantity',
            'tax',
            'associated'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            CommonTransactionLayout(),
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
                       href="{% url 'create-provider' %}?next={{ request.path|urlencode }}">
                        <span class="tf-icons bx bx-plus"></span>
                    </a>
                    """),
                    css_class="col-2 position-relative"
                ),
                css_class="row mb-3"
            ),
        )


class ServiceCreateForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = ('name',
                  'description',
                  'category',
                  'sell_tax',
                  'suggested_price',)

    def __init__(self, *args, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
            kwargs.pop('title')
        else:
            self.title = _("Create Service")

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
                                Field('category', css_class="form-select")
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
                                Field(
                                    PrependedText('suggested_price', '$')
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


class SendMailForm(forms.Form):
    send_copy = forms.BooleanField(initial=True, required=False)
    mail_address = forms.EmailField()

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
                Field('mail_address'),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('send_copy'),
                    css_class="col-6"
                ),
                Div(
                    ButtonHolder(
                        Submit('submit', 'Enviar',
                               css_class='btn btn-success float-end')
                    ),
                    css_class="col-6"
                ),
                css_class="row mb-3"
            ),
        )


class ExpenseCreateForm(BaseForm):

    class Meta:
        model = Expense
        fields = ('concept',
                  'image',
                  'description',
                  'cost',
                  'associated',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                                href="{% url 'select-provider' %}?next={{ request.path|urlencode }}">
                                    <span class="tf-icons bx bx-plus"></span>
                                </a>
                                """),
                    css_class="col-2 position-relative"
                ),
                css_class="row mb-3"
            ),
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
            ),
            Div(
                Div(
                    Field('concept')
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
                    Field(
                        PrependedText('cost', '$')
                    )
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar',
                       css_class='btn btn-success')
            )
        )
