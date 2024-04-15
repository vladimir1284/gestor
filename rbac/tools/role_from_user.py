from django.contrib.auth.models import Group
from django.contrib.auth.models import User


def create_role_from_user(user_id: int, role_name: str, rec: bool = True):
    user = User.objects.filter(id=user_id).last()
    if user is None:
        return {
            "error": "User not found",
        }

    if role_name == "":
        return {
            "error": "Please, insert a role name",
        }

    if Group.objects.filter(name=role_name).exists():
        return {
            "error": f"A role with name {role_name} already exists",
        }

    perms = [p for p in user.user_permissions.all()]
    if rec:
        for g in user.groups.all():
            for p in g.permissions.all():
                if p not in perms:
                    perms.append(p)

    role = Group.objects.create(
        name=role_name,
    )
    role.permissions.set(perms)
    role.save()
    return {
        "role_id": role.id,
    }
