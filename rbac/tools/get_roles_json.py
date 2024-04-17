import json

from django.contrib.auth.models import Group


def get_bind_name(name: str) -> str:
    return (
        name.replace(".", "___")
        .replace("/", "__")
        .replace("-", "_")
        .replace("+", "PARAM")
    )


def get_roles_json() -> str:
    roles = Group.objects.all()
    droles = []
    for r in roles:
        rol = {
            "id": r.id,
            "name": r.name,
            "permissions": [
                get_bind_name(f"{p.content_type.app_label}.{p.codename}")
                for p in r.permissions.all()
            ],
        }
        droles.append(rol)

    jr = json.dumps(droles)
    return jr
