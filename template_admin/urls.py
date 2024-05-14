from django.urls import path

from template_admin.views.template_edit import template_edit
from template_admin.views.template_list import template_list
from template_admin.views.template_remove import template_remove
from template_admin.views.template_version_create import template_create
from template_admin.views.template_version_edit import template_version_edit
from template_admin.views.template_version_export import template_version_export
from template_admin.views.template_version_import import template_version_import
from template_admin.views.template_version_new import template_version_new
from template_admin.views.template_version_options import template_version_options

urlpatterns = [
    path("template-list/", template_list, name="template-list"),
    path("template-list/<custom>", template_list, name="template-list"),
    path("template-edit/<id>", template_edit, name="template-edit"),
    path(
        "template-version-create",
        template_create,
        name="template-version-create",
    ),
    path(
        "template-version-create/<id>",
        template_create,
        name="template-version-create",
    ),
    path(
        "template-version-remove/<id>",
        template_remove,
        name="template-version-remove",
    ),
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
    path(
        "template-version-export/<id>",
        template_version_export,
        name="template-version-export",
    ),
    path(
        "template-version-import/<id>",
        template_version_import,
        name="template-version-import",
    ),
    path(
        "template-version-import/<id>/<custom>",
        template_version_import,
        name="template-version-import",
    ),
]
