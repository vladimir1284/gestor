from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


class RoleForm(forms.Form):
    def __init__(self, *args, role: Group | None = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial["name"] = "" if role is None else role.name
        self.fields["name"] = forms.CharField(max_length=150)

        menu = Permission.objects.filter(
            content_type__model="rbac", content_type__app_label="menu"
        )
        menuDiv = Div()
        for mp in menu:
            name = f"{mp.content_type.app_label}.{mp.codename}"

            if role is not None:
                self.initial[name] = role.permissions.filter(id=mp.id).exists()
            else:
                self.initial[name] = True

            self.fields[name] = forms.BooleanField(
                required=False,
                label=mp.name,
            )
            menuDiv.fields.append(Div(Field(name), css_class="mb-2"))

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(Field("name"), css_class="mb-2"),
            Div(
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header">
                            <button
                            data-bs-target="#menu_perms"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                Menu permissions
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            menuDiv,
                            css_class="accordion-body",
                        ),
                        css_id="menu_perms",
                        css_class="accordion-collapse collapse",
                    ),
                    css_class="accordion-item",
                ),
                css_class="accordion mb-4",
            ),
            ButtonHolder(
                Submit(
                    "submit",
                    "Save",
                    css_class="btn btn-success",
                ),
                # css_class="position-absolute top-0 end-0 pt-3 pe-3",
            ),
        )
