from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Submit
from django import forms

from template_admin.models.template_version import TemplateVersion


class CreateTemplateVersionForm(forms.ModelForm):
    class Meta:
        model = TemplateVersion
        fields = [
            "module",
            "template",
            "language",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            PrependedText("module", mark_safe("<i class='bx bx-cog' ></i>")),
            PrependedText("template", mark_safe("<i class='bx bx-layout' ></i>")),
            PrependedText("language", mark_safe("<i class='bx bx-world'></i>")),
            ButtonHolder(Submit("submit", "Save", css_class="btn btn-success")),
        )
