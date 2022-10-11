from django.forms import ModelForm
from django import forms
from .models import *
from django.core.files.images import get_image_dimensions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',
                  'password1',
                  'password2',
                  'first_name',
                  'last_name',
                  #   'phone_number',
                  'email')
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo',
            'username': 'Usuario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        # if len(errorList) == 0:
        #     self.fields['first_name'].widget.attrs.update(
        #         {'autofocus': 'autofocus'})
        # else:
        for item in errorList:
            self.fields[item].widget.attrs.update({'autofocus': ''})
            break
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Juan'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Pérez'})
        self.fields['email'].widget.attrs.update({'placeholder': 'juan.perez'})
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'juan.perez'})
        self.fields['username'].help_text = '''
        Requerido. 150 caracteres o menos. Letras, dígitos y @ /./+/-/_ solamente.
        '''
        self.fields['password1'].help_text = '''
        <ul>
            <li>La contraseña no puede ser similar a la información personal.</li>
            <li>La contraseña debe tener al menos 8 caracteres.</li>
            <li>La contraseña no puede ser eneramente numérica.</li>
        </ul>
        '''
        self.fields['password2'].help_text = '''
        Introduzca nuevamente su contraseña.
        '''
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmar"

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = 'col-sm-2 form-label'
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText('username',
                                  '<i class="bx bx-user-circle"></i>'),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('first_name',
                                  '<i class="bx bx-user"></i>'),
                    css_class='form-control'
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
                    PrependedAppendedText('email',
                                          '<i class="bx bx-envelope"></i>',
                                          '@ejemplo.com'),
                    css_class='form-control'
                ),
                Div(
                    HTML('Puede usar letras, números y puntos'),
                    css_class="form-text"
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    'password1',
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    'password2',
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'role', 'phone_number')
        labels = {
            'avatar': 'Imágen',
            'role': 'Rol',
            'phone_number': 'Teléfono'
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
        self.helper.label_class = 'col-sm-2 form-label'
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText('phone_number',
                                  '<i class="bx bx-phone"></i>'),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Field(
                    PrependedText('role',
                                  '<i class="bx bx-certification"></i>',
                                  css_class="form-select"),
                    css_class='form-control'
                ),
                css_class="row mb-3"
            ),
            Div(
                Div(
                    Field('avatar',
                          css_class='form-control'
                          )
                ),
                css_class="mb-3"
            ),
            ButtonHolder(
                Submit('submit', 'Enviar', css_class='btn btn-success')
            )
        )


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'type': 'password'
    }))

