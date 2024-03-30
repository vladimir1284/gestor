from django.contrib.auth.models import Permission


def get_role_menu_perms(data: dict) -> list[Permission]:
    menu = Permission.objects.filter(
        content_type__model="rbac", content_type__app_label="menu"
    )

    perms: list[Permission] = []
    for mp in menu:
        name = f"{mp.content_type.app_label}.{mp.codename}"
        if data[name]:
            perms.append(mp)

    return perms
