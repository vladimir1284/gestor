from django import forms

from rent.models.vehicle import Trailer
from services.tools.available_positions import get_available_positions


class TrailerChangePosForm(forms.Form):
    def __init__(self, *args, trailer: Trailer, **kwargs):
        super().__init__(*args, **kwargs)
        position = trailer.position

        positions = get_available_positions(
            current_pos=position,
            null=True,
            storage=True,
            unselected=True,
        )

        self.fields["position"] = forms.ChoiceField(
            required=False,
            choices=positions,
            # initial=position,
            initial="-",
        )
        self.fields["note"] = forms.CharField(
            widget=forms.Textarea(
                attrs={"rows": 3},
            ),
            required=False,
        )

    def clean_position(self):
        valor = self.cleaned_data.get("position")
        if valor == "-":
            raise forms.ValidationError("Please, select a position")
        return valor

    def clean_position_note(self):
        valor = self.cleaned_data.get("position_note")
        if valor is None:
            return ""
        return valor
