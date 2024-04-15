from django.contrib.auth.models import Permission


def get_role_perms(data: dict, label: str) -> list[Permission]:
    permissiions = Permission.objects.filter(
        content_type__model="rbac", content_type__app_label=label
    )

    perms: list[Permission] = []
    for perm in permissiions:
        name = f"{perm.content_type.app_label}.{perm.codename}"
        if data[name]:
            perms.append(perm)

    return perms


def get_role_perms_all(data: dict) -> list[Permission]:
    perms = []
    perms += get_role_perms(data, "menu")
    perms += get_role_perms(data, "urls")
    perms += get_role_perms(data, "dashboard_card")
    perms += get_role_perms(data, "extra_perm")
    return perms
