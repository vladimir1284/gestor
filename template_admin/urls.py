from django.urls import path

from template_admin.views.template_edit import template_edit
from template_admin.views.template_list import template_list
from template_admin.views.template_version_edit import template_version_edit
from template_admin.views.template_version_new import template_version_new
from template_admin.views.template_version_options import \
    template_version_options

urlpatterns = [
    path("template-list", template_list, name="template-list"),
    path("template-edit/<id>", template_edit, name="template-edit"),
    path(
        "template-version-new/<id>",
        template_version_new,
        name="template-version-new",
    ),
    path(
        "template-version-edit/<id>",
        template_version_edit,
        name="template-version-edit",
    ),
    path(
        "template-version-edit/<id>/<version>",
        template_version_edit,
        name="template-version-edit",
    ),
    path(
        "template-version-options/<id>/<version>",
        template_version_options,
        name="template-version-options",
    ),
]
