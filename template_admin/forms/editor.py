from django import forms


class TextEditorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"] = forms.CharField(
            widget=forms.Textarea,
            label="",
        )


class ListEditorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"] = forms.CharField(
            widget=forms.HiddenInput,
            label="",
        )
