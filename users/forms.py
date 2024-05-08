from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from phonenumber_field.widgets import RegionalPhoneNumberWidget

from .models import *


class CommonUserLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Field(
                    PrependedText("first_name", mark_safe('<i class="bx bx-user"></i>'))
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText("last_name", mark_safe('<i class="bx bx-user"></i>')),
                    css_class="form-control",
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "username", mark_safe('<i class="bx bx-user-circle"></i>')
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "email",
                        mark_safe('<i class="bx bx-envelope"></i>'),
                        "@ejemplo.com",
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "groups",
                        mark_safe('<i class="bx bx-cog"></i>'),
                    ),
                ),
                css_class="row mb-3",
            ),
        )


class CommonContactLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            PictureLayout(),
            Div(
                Field(
                    PrependedText(
                        "name", mark_safe('<i class="bx bx-user-circle"></i>')
                    )
                )
            ),
            # Div(
            #     Field(
            #         PrependedText(
            #             "alias", mark_safe('<i class="bx bx-user-circle"></i>')
            #         )
            #     ),
            #     css_class="row mb-3",
            # ),
            Div(
                Field(
                    PrependedText(
                        "phone_number", mark_safe('<i class="bx bx-phone"></i>')
                    )
                ),
                css_class="row",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "email",
                        mark_safe('<i class="bx bx-envelope"></i>'),
                        "@ejemplo.com",
                    )
                ),
                css_class="row mb-3",
            ),
            Div(Field("language", css_class="form-select")),
            # Div(Field("state", css_class="form-select")),
            # Div(Field("other_state"), css_class="row mb-3"),
            # Div(Field("city", css_class="form-select"), css_class="row"),
            # Div(Field("other_city"), css_class="row mb-3"),
            # Div(Div(Field("note", rows="2")), css_class="mb-3"),
            # Div(
            #     Div(Field("membership"), css_class="col-6"),
            #     Div(Field("active"), css_class="col-6"),
            #     css_class="mb-3 row",
            # ),
        )


class PictureLayout(Layout):
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
                    src="{% static 'assets/img/icons/user.png' %}"
                {% endif %}>
                """
                ),
                css_class="d-flex align-items-start align-items-sm-center gap-4",
            ),
            Div(Div(Field("avatar")), css_class="mb-3"),
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["groups"].label = "System roles"
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        # self.helper.css = 'is-invalid'
        self.helper.layout = Layout(
            CommonUserLayout(),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "email",
            "groups",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        self.fields["username"].widget.attrs.pop("autofocus", None)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": "autofocus"})
            break
        self.fields["first_name"].widget.attrs.update({"placeholder": _("John")})
        self.fields["last_name"].widget.attrs.update({"placeholder": _("Doe")})
        self.fields["email"].widget.attrs.update({"placeholder": _("john.doe")})
        self.fields["username"].widget.attrs.update({"placeholder": _("john.doe")})
        self.fields["groups"].label = "System roles"
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            CommonUserLayout(),
            Div(Field("password1"), css_class="row mb-3"),
            Div(Field("password2"), css_class="row mb-3"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "role", "phone_number")
        labels = {
            "role": _("role"),
            "phone_number": _("phone number"),
            "avatar": _("profile image"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone_number"].widget = RegionalPhoneNumberWidget(region="US")
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": ""})
            break
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            PictureLayout(),
            Div(
                Field(
                    PrependedText(
                        "phone_number", mark_safe('<i class="bx bx-phone"></i>')
                    )
                ),
                css_class="row",
            ),
            Div(
                Field(
                    PrependedText(
                        "role",
                        mark_safe('<i class="bx bx-certification"></i>'),
                        css_class="form-select",
                    )
                ),
                css_class="row mb-3",
            ),
        )


class BaseContactForm(forms.ModelForm):
    class Meta:
        model = Associated
        fields = [
            "avatar",
            "name",
            "phone_number",
            "email",
            "language",
            # "alias",
            # "state",
            # "city",
            # "other_state",
            # "other_city",
            # "note",
            # "membership",
            # "active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone_number"].widget = RegionalPhoneNumberWidget(region="US")
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": "autofocus"})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"


class AssociatedCreateForm(BaseContactForm):
    class Meta(BaseContactForm.Meta):
        model = Associated
        fields = BaseContactForm.Meta.fields + ["type"]

    def __init__(self, *args, only_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["type"].widget = HiddenInput()
        self.fields["phone_number"].required = True
        self.fields["email"].required = True

        if only_fields is not None and len(only_fields) != 0 and only_fields[0] != "":
            for field in self.fields:
                if field not in only_fields:
                    self.fields[field].widget = HiddenInput()

        self.helper.layout = Layout(
            CommonContactLayout(),
            Field("type"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class ProviderCreateForm(AssociatedCreateForm):
    class Meta(AssociatedCreateForm.Meta):
        fields = AssociatedCreateForm.Meta.fields + ["outsource", "alias", "membership"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["type"].widget = HiddenInput()
        self.fields["alias"].widget = HiddenInput()
        self.fields["membership"].widget = HiddenInput()

        self.helper.layout = Layout(
            CommonContactLayout(),
            Field("alias"),
            Field("membership"),
            Field("type"),
            Div(Field("outsource"), css_class="mb-3"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class CompanyCreateForm(BaseContactForm):
    class Meta(BaseContactForm.Meta):
        model = Company
        fields = BaseContactForm.Meta.fields + ["vehicles"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["alias"].widget = HiddenInput()

        self.helper.layout = Layout(
            CommonContactLayout(),
            Div(Field("vehicles", css_class="form-select"), css_class="row mb-3"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )
