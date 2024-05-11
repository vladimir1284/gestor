from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse

from services.models import Associated


class LesseeContactForm(forms.ModelForm):
    def __init__(self, *args, use_client_url: dict | None = None, **kwargs):
        self.use_client_url = use_client_url
        self.buttons = ButtonHolder(
            Submit(
                "submit",
                "Next",
                css_class="btn btn-success",
            ),
        )

        super().__init__(*args, **kwargs)

        self.fields["name"].required = True
        self.fields["phone_number"].required = True
        self.fields["language"].required = True
        self.fields["email"].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(Field("name"), css_class="mb-2"),
            Div(Field("phone_number"), css_class="mb-2"),
            Div(Field("language"), css_class="mb-2"),
            Div(Field("email"), css_class="mb-2"),
            self.buttons,
        )

    class Meta:
        model = Associated
        fields = ("name", "phone_number", "language", "email")

    def validate_client(self):
        if self.use_client_url is None or "url" not in self.use_client_url:
            return

        phone = self.cleaned_data["phone_number"]
        client = Associated.objects.filter(phone_number=phone).last()
        if client is None:
            return

        url_name = self.use_client_url["url"]
        args: list = []
        if "args" in self.use_client_url:
            args: list = self.use_client_url["args"]
            try:
                idx = args.index("{client_id}")
                args[idx] = client.id
            except Exception:
                pass

        if "on_exists" in self.use_client_url:
            url_name, args = self.use_client_url["on_exists"](args=args, client=client)

        url = reverse(url_name, args=args)
        self.buttons.append(
            HTML(
                f"""<a class='btn btn-outline-primary' href='{url}'>
                Use client
                <strong>{client.name}</strong>
                with phone number
                <strong>{client.phone_number}</strong>
                </a>"""
            )
        )

    def clean(self):
        self.validate_client()
        return super().clean()
