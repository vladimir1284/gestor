from django.forms import ModelForm
from django import forms
from rent.models.lease import HandWriting


class HandWritingForm(ModelForm):
    class Meta:
        model = HandWriting
        fields = ("img",)  # 'position', 'lease')

    img = forms.CharField(max_length=2000000)
