from django.contrib.auth.models import Permission


def get_role_urls_perms(data: dict) -> list[Permission]:
    urls = Permission.objects.filter(
        content_type__model="rbac", content_type__app_label="urls"
    )

    perms: list[Permission] = []
    for up in urls:
        name = f"{up.content_type.app_label}.{up.codename}"
        if data[name]:
            perms.append(up)

    return perms
