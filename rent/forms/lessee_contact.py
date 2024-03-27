from django import forms

from services.models import Associated


class LesseeContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["phone_number"].required = True
        self.fields["language"].required = True
        self.fields["email"].required = False

    class Meta:
        model = Associated
        fields = ("name", "phone_number", "language", "email")
