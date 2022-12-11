from django.forms import ModelForm, HiddenInput
from django import forms
from .models import *
from django.core.files.images import get_image_dimensions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class CommonUserLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Field(
                    PrependedText('first_name',
                                  '<i class="bx bx-user"></i>')
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('last_name',
                                  '<i class="bx bx-user"></i>'),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('username',
                                  '<i class="bx bx-user-circle"></i>')
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
            )
        )


class CommonContactLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            CommonProfileLayout(),
            Div(
                Field(
                    PrependedText('name',
                                  '<i class="bx bx-user-circle"></i>')
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
            )
        )


class CommonProfileLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                HTML(
                    """
                {% load static %}
                <img id="preview" 
                alt="user-avatar" 
                class="d-block rounded" 
                height="100" width="100"
                {% if form.avatar.value %}
                    src="/media/{{ form.avatar.value }}"
                {% else %}  
                    src="{% static 'images/icons/client.png' %}"
                {% endif %}>
                """
                ),
                css_class="d-flex align-items-start align-items-sm-center gap-4"
            ),
            Div(
                Div(
                    Field('avatar')
                ),
                css_class="mb-3"
            ),
            Div(
                Field(
                    PrependedText('phone_number',
                                  '<i class="bx bx-phone"></i>')
                ),
                css_class="row"
            )
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        # self.helper.css = 'is-invalid'
        self.helper.layout = Layout(
            CommonUserLayout(),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username',
                  'password1',
                  'password2',
                  'first_name',
                  'last_name',
                  'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        self.fields['username'].widget.attrs.pop("autofocus", None)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': 'autofocus'})
            break
        self.fields['first_name'].widget.attrs.update(
            {'placeholder': _('John')})
        self.fields['last_name'].widget.attrs.update({'placeholder': _('Doe')})
        self.fields['email'].widget.attrs.update(
            {'placeholder': _('john.doe')})
        self.fields['username'].widget.attrs.update(
            {'placeholder': _('john.doe')})
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            CommonUserLayout(),
            Div(
                Field(
                    'password1'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    'password2'
                ),
                css_class="row mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('avatar', 'role', 'phone_number')
        labels = {
            'role': _('role'),
            'phone_number': _('phone number'),
            'avatar': _('profile image'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': ''})
            break
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            CommonProfileLayout(),
            Div(
                Field(
                    PrependedText('role',
                                  '<i class="bx bx-certification"></i>',
                                  css_class="form-select")
                ),
                css_class="row mb-3"
            )
        )


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
        self.fields['type'].widget = HiddenInput()

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'form-label'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText('company',
                                      '<i class="bx bx-buildings"></i>',
                                      css_class="form-select")
                    ),
                    css_class="col-10"
                ),
                Div(
                    HTML(
                        """
                    <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                       type="button"
                       href="{% url 'select-company' %}?next={{ request.path|urlencode }}"
                       data-bs-toggle="tooltip"
                       data-bs-offset="0,4"
                       data-bs-placement="left"
                       data-bs-html="true"
                       title=""
                       data-bs-original-title="<span>Modify company</span>">
                        <span class="tf-icons bx bx-plus"></span>
                    </a>
                    """),
                    css_class="col-2 position-relative"
                ),
                css_class="row mb-3"
            ),
            CommonContactLayout(),
            Field('type'),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class CompanyCreateForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = (
            'name',
            'address',
            'note',
            'email',
            'avatar',
            'phone_number'
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
            CommonContactLayout(),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )
