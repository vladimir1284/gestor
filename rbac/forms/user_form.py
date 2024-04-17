from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.helper import Layout
from crispy_forms.helper import mark_safe
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "groups",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"] = forms.ModelMultipleChoiceField(
            queryset=Group.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="",
        )

        instance = kwargs["instance"] if "instance" in kwargs else None
        perms = Permission.objects.filter(
            content_type__model="rbac", content_type__app_label="menu"
        ).order_by("name")
        menuDiv = Div()
        for perm in perms:
            name = f"{perm.content_type.app_label}.{perm.codename}"

            if instance is not None:
                self.initial[name] = instance.user_permissions.filter(
                    id=perm.id
                ).exists()
            else:
                self.initial[name] = True

            self.fields[name] = forms.BooleanField(
                required=False,
                label=perm.name,
            )
            menuDiv.fields.append(Div(Field(name), css_class="mb-2"))

        perms = Permission.objects.filter(
            content_type__model="rbac", content_type__app_label="urls"
        ).order_by("name")
        urlsDiv = Div()
        for perm in perms:
            name = f"{perm.content_type.app_label}.{perm.codename}"

            if instance is not None:
                self.initial[name] = instance.user_permissions.filter(
                    id=perm.id
                ).exists()
            else:
                self.initial[name] = True

            self.fields[name] = forms.BooleanField(
                required=False,
                label=perm.name,
            )
            urlsDiv.fields.append(Div(Field(name), css_class="mb-2"))

        perms = Permission.objects.filter(
            content_type__model="rbac",
            content_type__app_label="dashboard_card",
        ).order_by("name")
        dashCardDiv = Div()
        for perm in perms:
            name = f"{perm.content_type.app_label}.{perm.codename}"

            if instance is not None:
                self.initial[name] = instance.user_permissions.filter(
                    id=perm.id
                ).exists()
            else:
                self.initial[name] = True

            self.fields[name] = forms.BooleanField(
                required=False,
                label=perm.name,
            )
            dashCardDiv.fields.append(Div(Field(name), css_class="mb-2"))

        perms = Permission.objects.filter(
            content_type__model="rbac",
            content_type__app_label="extra_perm",
        ).order_by("name")
        extraPermDiv = Div()
        for perm in perms:
            name = f"{perm.content_type.app_label}.{perm.codename}"

            if instance is not None:
                self.initial[name] = instance.user_permissions.filter(
                    id=perm.id
                ).exists()
            else:
                self.initial[name] = True

            self.fields[name] = forms.BooleanField(
                required=False,
                label=perm.name,
            )
            extraPermDiv.fields.append(Div(Field(name), css_class="mb-2"))

        # self.fields["groups"].label = "Roles"
        # self.fields["groups"].widget = forms.CheckboxSelectMultiple()
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(
                Field(
                    PrependedText(
                        "username",
                        mark_safe('<i class="bx bx-user-circle"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "first_name",
                        mark_safe('<i class="bx bx-user"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            Div(
                Field(
                    PrependedText(
                        "last_name",
                        mark_safe('<i class="bx bx-user"></i>'),
                    )
                ),
                css_class="row mb-3",
            ),
            # Div(
            #     Field(
            #         "groups",
            #         # PrependedText(
            #         #     "groups",
            #         #     mark_safe('<i class="bx bx-cog"></i>'),
            #         # )
            #     ),
            #     css_class="row mb-3",
            # ),
            Div(
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
                            <button
                            data-bs-target="#groups"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                Roles
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            Field("groups"),
                            css_class="accordion-body",
                        ),
                        css_id="groups",
                        css_class="accordion-collapse collapse",
                    ),
                    css_id="groups-accordion",
                    css_class="accordion-item border-bottom",
                ),
                css_id="others-accordion",
                css_class="accordion mb-4 border rounded",
            ),
            # ButtonHolder(
            #     Submit(
            #         "submit",
            #         "Enviar",
            #         css_class="btn btn-success",
            #     ),
            # ),
            Div(
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
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
                    css_id="menu-accordion",
                    css_class="accordion-item border-bottom",
                ),
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
                            <button
                            data-bs-target="#urls_perms"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                URLS permissions
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            urlsDiv,
                            css_class="accordion-body",
                        ),
                        css_id="urls_perms",
                        css_class="accordion-collapse collapse",
                    ),
                    css_id="urls-accordion",
                    css_class="accordion-item border-bottom",
                ),
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
                            <button
                            data-bs-target="#dashboard_card_perms"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                Dashboard cards permissions
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            dashCardDiv,
                            css_class="accordion-body",
                        ),
                        css_id="dashboard_card_perms",
                        css_class="accordion-collapse collapse",
                    ),
                    css_id="dashcards-accordion",
                    css_class="accordion-item border-bottom",
                ),
                Div(
                    HTML(
                        """
                            <h2 class="accordion-header d-flex">
                            <input type="checkbox" class="mark-all checkboxinput">
                            <button
                            data-bs-target="#extra_perms"
                            class="accordion-button collapsed text-primary"
                            type="button"
                            data-bs-toggle="collapse">
                                Other permissions
                            </button>
                            </h2>
                        """
                    ),
                    Div(
                        Div(
                            extraPermDiv,
                            css_class="accordion-body",
                        ),
                        css_id="extra_perms",
                        css_class="accordion-collapse collapse",
                    ),
                    css_class="accordion-item",
                ),
                css_id="others-accordion",
                css_class="accordion mb-4 border rounded",
            ),
        )
