from django.forms import ModelForm
from ..models.tracker import Tracker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML
from crispy_forms.bootstrap import PrependedText, AppendedText


class TrackerForm(ModelForm):
    class Meta:
        model = Tracker
        fields = ('trailer', 'imei',  'device_password',
                  'device_id', 'Mode', 'Tint', 'TGPS', 'Tsend')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Tracker device',
                Div(
                    Div(
                        'imei',
                        css_class='col-m-4'
                    ),
                    Div(
                        'device_password',
                        css_class='col-m-4'
                    ),
                    Div(
                        'device_id',
                        css_class='col-m-4'
                    ),
                    css_class='row'
                )
            ),
            Div(
                'Mode',
                css_class='row'
            ),
            Fieldset(
                'Time intervals',
                Div(
                    Div(
                        AppendedText('Tint', "min"),
                        css_class='col-4'
                    ),
                    Div(
                        AppendedText('Tsend', "min"),
                        css_class='col-4'
                    ),
                    Div(
                        AppendedText('TGPS', "min"),
                        css_class='col-4'
                    ),
                    css_class='row'
                )
            ),
            ButtonHolder(
                Submit('submit', 'Send',
                       css_class='btn btn-success')
            )

        )
