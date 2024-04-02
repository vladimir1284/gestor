from django.urls import path

from rbac.views.delete_role import delete_role
from rbac.views.delete_user import delete_user
from rbac.views.list_roles import list_roles
from rbac.views.list_users import list_users
from rbac.views.role_form import role_form
from rbac.views.user_change_password import user_change_password
from rbac.views.user_form import user_create
from rbac.views.user_form import user_update


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
    path(
        "list-users/",
        list_users,
        name="rbac-list-users",
    ),
    path(
        "user-create/",
        user_create,
        name="rbac-user-create",
    ),
    path(
        "user-update/<id>",
        user_update,
        name="rbac-user-update",
    ),
    path(
        "user-delete/<id>",
        delete_user,
        name="rbac-user-delete",
    ),
    path(
        "user-password/<id>",
        user_change_password,
        name="rbac-user-pass",
    ),
]
