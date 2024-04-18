from crispy_forms.bootstrap import PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm


class SetUserPassForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields["new_password1"].widget.attrs["x-bind"] = "pass1"
        self.fields["new_password2"].widget.attrs["x-bind"] = "pass2"

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedAppendedText(
                        "new_password1",
                        mark_safe('<i class="bx bxs-key" ></i>'),
                        mark_safe(
                            '<i class="bx bx-hide" x-bind="butPass1"></i>',
                        ),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "new_password2",
                        mark_safe('<i class="bx bxs-key" ></i>'),
                        mark_safe(
                            '<i class="bx bx-hide" x-bind="butPass2"></i>',
                        ),
                    )
                ),
                css_class="row mb-3",
            ),
        )


class ChangeUserPassForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields["old_password"].widget.attrs["x-bind"] = "passO"
        self.fields["new_password1"].widget.attrs["x-bind"] = "pass1"
        self.fields["new_password2"].widget.attrs["x-bind"] = "pass2"

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedAppendedText(
                        "old_password",
                        mark_safe('<i class="bx bxs-key" ></i>'),
                        mark_safe(
                            '<i class="bx bx-hide" x-bind="butPassO"></i>',
                        ),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "new_password1",
                        mark_safe('<i class="bx bxs-key" ></i>'),
                        mark_safe(
                            '<i class="bx bx-hide" x-bind="butPass1"></i>',
                        ),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedAppendedText(
                        "new_password2",
                        mark_safe('<i class="bx bxs-key" ></i>'),
                        mark_safe(
                            '<i class="bx bx-hide" x-bind="butPass2"></i>',
                        ),
                    )
                ),
                css_class="row mb-3",
            ),
        )
