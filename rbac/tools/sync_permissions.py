from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from menu.menu.menu_element import PermissionParam
from rbac.tools.all_perms import init_permissions
from rbac.tools.all_perms import PERMS_MAP


def update_groups(p: Permission):
    groups: list[Group] = Group.objects.filter(permissions=p)
    for g in groups:
        g.permissions.add(p)
        g.save()


def sync_permission(ct: ContentType, p: PermissionParam):
    try:
        permission = Permission.objects.create(
            name=p.name,
            codename=p.code,
            content_type=ct,
        )
        update_groups(permission)
    except Exception as e:
        print(p.app, p.code, p.name)
        raise e


def sync_permissiions_of_ct(
    ct: ContentType,
    perms: list[PermissionParam],
    permissions: dict[str, Permission],
):
    for p in perms:
        if p.code not in permissions:
            sync_permission(ct, p)
        elif permissions[p.code].name != p.name:
            permissions[p.code].name = p.name
            permissions[p.code].save()


def get_content_types_map(labs: list[str]) -> dict[str, ContentType]:
    content_types = ContentType.objects.filter(app_label__in=labs, model="rbac")
    content_types_map = {}
    for content_type in content_types:
        content_types_map[content_type.app_label] = content_type
    return content_types_map


def get_content_types_map_for_labs(labs: list[str]) -> dict[str, ContentType]:
    content_types_map = get_content_types_map(labs)
    for lab in labs:
        if lab not in content_types_map:
            ct = ContentType.objects.create(app_label=lab, model="rbac")
            content_types_map[lab] = ct
    return content_types_map


def sync_permissions():
    init_permissions()

    labs = PERMS_MAP.keys()
    content_types_map = get_content_types_map_for_labs(labs)

    codes = []

    for lab, ps in PERMS_MAP.items():
        codes += [p.code for p in ps]

    permissions = Permission.objects.filter(
        content_type__in=content_types_map.values(),
    )
    permissions.exclude(codename__in=codes).delete()

    permissions_map = {}
    for perm in permissions:
        permissions_map[perm.codename] = perm

    for lab, ps in PERMS_MAP.items():
        ct = content_types_map[lab]

        sync_permissiions_of_ct(ct, ps, permissions_map)
