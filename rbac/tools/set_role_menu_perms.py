from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


def set_role_menu_perms(role: Group, data: dict):
    menu = Permission.objects.filter(
        content_type__model="rbac", content_type__app_label="menu"
    )

    perms: list[Permission] = []
    for mp in menu:
        name = f"{mp.content_type.app_label}.{mp.codename}"
        if data[name]:
            perms.append(mp)
    role.permissions.set(perms)
