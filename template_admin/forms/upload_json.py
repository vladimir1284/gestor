from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Submit
from django import forms


class UploadJsonForm(forms.Form):
    file = forms.FileField(
        required=True,
        allow_empty_file=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["file"].label = "JSON"

        self.helper = FormHelper()
        self.helper.field_class = "mb-3"
        self.helper.layout = Layout(
            AppendedText("file", mark_safe("<i class='bx bxs-file-json' ></i>")),
            ButtonHolder(Submit("submit", "Save", css_class="btn btn-success")),
        )
