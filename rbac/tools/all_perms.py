from collections import defaultdict

from menu.menu.menu import getMenuPermissions
from menu.menu.menu import PermissionParam
from rbac.tools.get_urls import get_urls_perms


PERMS: list[PermissionParam] = []
PERMS_MAP: dict[str, list[PermissionParam]
                ] = defaultdict(list[PermissionParam])


def init_permissions():
    global PERMS, PERMS_MAP

    menu_perms = getMenuPermissions()
    urls_perms = get_urls_perms()

    PERMS += menu_perms
    PERMS += urls_perms

    for p in PERMS:
        if p.app == "":
            continue
        PERMS_MAP[p.app].append(p)
