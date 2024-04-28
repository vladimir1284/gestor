from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.utils import timezone

from rent.models.vehicle import Manufacturer
from rent.models.vehicle import Trailer
from rent.models.vehicle import TrailerDocument
from rent.models.vehicle import TrailerPicture
from services.tools.available_positions import get_available_positions
from utils.forms import (
    BaseForm,
)


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ("brand_name", "url", "icon")

    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(Div(Field("brand_name")), css_class="mb-3"),
            Div(Div(Field("url")), css_class="mb-3"),
            Div(Div(Field("icon", css_class="form-select")), css_class="mb-3"),
            ButtonHolder(Submit("submit", "Enviar",
                         css_class="btn btn-success")),
        )


class TrailerCreateForm(BaseForm):
    class Meta:
        model = Trailer
        fields = (
            "note",
            "vin",
            "year",
            "cdl",
            "type",
            "plate",
            "manufacturer",
            "axis_number",
            "load",
            "lease_to_own",
            "active",
            "position",
            "position_note",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.field_class = "mb-3"

        pos_readonly = self.instance.pos_readonly
        availables_positions = get_available_positions(
            current_pos=self.instance.position,
            null=True,
            # unselected=not pos_readonly,
        )
        self.initial["position"] = self.instance.position
        self.initial["position_note"] = self.instance.position_note
        self.fields["position"].widget = forms.Select(
            choices=availables_positions,
        )
        self.fields["position_note"].required = False
        self.fields["position_note"].widget.attrs["rows"] = 2
        if pos_readonly:
            self.fields["position"].widget.attrs["readonly"] = True
            self.fields["position"].widget.attrs["disabled"] = True
            self.fields["position_note"].widget.attrs["readonly"] = True
            self.fields["position_note"].widget.attrs["disabled"] = True

        self.helper.layout = Layout(
            Field("manufacturer"),
            Field("type"),
            Field("year"),
            Field("vin"),
            Field("plate"),
            Field(
                AppendedText(
                    "position",
                    (
                        ""
                        if self.instance.position_date is None
                        else self.instance.position_date.strftime("%b %d, %Y")
                    ),
                ),
            ),
            Field("position_note"),
            Field("cdl"),
            Field("axis_number"),
            Field("load"),
            Field("note", rows="2"),
            Field("lease_to_own"),
            Field("active"),
            ButtonHolder(Submit("submit", "Enviar",
                         css_class="btn btn-success")),
        )

    def clean_position_note(self):
        position_note = self.cleaned_data["position_note"]
        if position_note is None:
            return ""
        return position_note


class TrailerPictureForm(forms.ModelForm):
    class Meta:
        model = TrailerPicture
        fields = ("image",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(Field("image"), css_class="row mb-3"),
            ButtonHolder(Submit("submit", "Enviar",
                         css_class="btn btn-success")),
        )


class CommonDocumentLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Fieldset(
                "Document Information",
                Div(Field("name", placeholder="Name"), css_class="mb-3"),
                Div(Field("file", placeholder="Name"), css_class="mb-3"),
                Div(Field("note", placeholder="Note", rows="2"), css_class="mb-3"),
                Div(Field("is_active"), css_class="mb-3"),
                css_class="row mb-3",
            )
        )


class TrailerDocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = TrailerDocument
        fields = ("name", "note", "file", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            CommonDocumentLayout(),
            ButtonHolder(Submit("submit", "Enviar",
                         css_class="btn btn-success")),
        )


class TrailerDocumentForm(forms.ModelForm):
    class Meta:
        model = TrailerDocument
        fields = (
            "name",
            "note",
            "file",
            "expiration_date",
            "remainder_days",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["expiration_date"] = forms.DateTimeField(
            widget=forms.DateInput(
                attrs={"type": "date"},
            ),
            required=False,
        )
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            CommonDocumentLayout(),
            Div(Field("expiration_date"), css_class="mb-3"),
            Div(
                Field("remainder_days", placeholder="Remainder days"), css_class="mb-3"
            ),
            ButtonHolder(Submit("submit", "Enviar",
                         css_class="btn btn-success")),
        )

    def clean(self):
        cleaned_data = super().clean()
        expiration_date = cleaned_data.get("expiration_date")
        remainder_days = cleaned_data.get("remainder_days")
        if remainder_days and expiration_date:
            remainder_date = expiration_date - \
                timezone.timedelta(days=remainder_days)
            if remainder_date < timezone.now():
                raise forms.ValidationError(
                    "Reminder date cannot be in the past.")
        return cleaned_data
