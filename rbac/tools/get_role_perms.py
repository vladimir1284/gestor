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
