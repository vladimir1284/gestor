from django.urls import path

from rbac.tools.sync_permissions import sync_permissions
from rbac.views.delete_role import delete_role
from rbac.views.list_roles import list_roles
from rbac.views.role_form import role_form


sync_permissions()

urlpatterns = [
    path(
        "list-roles/",
        list_roles,
        name="rbac-list-roles",
    ),
    path(
        "role-form/",
        role_form,
        name="rbac-role-form",
    ),
    path(
        "role-form/<id>",
        role_form,
        name="rbac-role-form",
    ),
    path(
        "role-delete/<id>",
        delete_role,
        name="rbac-role-delete",
    ),
]
