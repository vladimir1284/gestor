from django.urls import path

from rbac.tools.sync_permissions import sync_permissions
from rbac.views.list_roles import list_roles


sync_permissions()

urlpatterns = [
    path(
        "list-roles/",
        list_roles,
        name="rbac-list-roles",
    ),
]
