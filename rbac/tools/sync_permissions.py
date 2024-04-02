from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from menu.menu.menu_element import PermissionParam
from rbac.tools.all_perms import init_permissions
from rbac.tools.all_perms import PERMS_MAP


def update_groups(p: Permission):
    groups: list[Group] = Group.objects.all()
    for g in groups:
        if g.permissions.filter(id=p.id).exists():
            continue
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


def sync_permissiions_of_ct(ct: ContentType, perms: list[PermissionParam]):
    for p in perms:
        perm = Permission.objects.filter(
            codename=p.code,
            content_type=ct,
        ).first()
        if perm is None:
            sync_permission(ct, p)
        else:
            perm.name = p.name
            perm.save()


def sync_permissions():
    init_permissions()

    for lab, ps in PERMS_MAP.items():
        ct, _ = ContentType.objects.get_or_create(app_label=lab, model="rbac")

        codes = [p.code for p in ps]
        Permission.objects.filter(
            content_type__app_label=lab, content_type__model="rbac"
        ).exclude(codename__in=codes).delete()

        sync_permissiions_of_ct(ct, ps)
