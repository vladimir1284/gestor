from django import forms
from crispy_forms.bootstrap import PrependedText
import phonenumbers
from .models.crm_model import FlaggedCalls
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder, Div, Field, HTML
from django.utils.safestring import mark_safe
from users.forms import AssociatedCreateForm


class CommonContactLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            PictureLayout(),
            Div(
                Field(
                    PrependedText(
                        "phone_number",
                        mark_safe('<i class="bx bx-phone"></i>'),
                        attrs={"readonly": "readonly"},
                    )
                ),
                css_class="row",
            ),
            Div(
                Field("list_type"),
                Field("reason"),
                css_class="row",
            ),
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


class FlaggedCallsForm(forms.ModelForm):
    class Meta:
        model = FlaggedCalls
        fields = ["phone_number", "list_type", "reason"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super(FlaggedCallsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # No renderizar la etiqueta del formulario
        self.helper.disable_csrf = True  # No renderizar el token CSRF
        self.helper.layout = Layout(
            CommonContactLayout(),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class AssociatedCreateFormCrm(AssociatedCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo phone_number sea de solo lectura
        self.fields["phone_number"].widget = forms.TextInput(attrs={"readonly": True})
