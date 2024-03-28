from collections import defaultdict

from menu.menu.menu import getMenuPermissions
from menu.menu.menu import PermissionParam


PERMS: list[PermissionParam] = []
PERMS_MAP: dict[str, list[PermissionParam]
                ] = defaultdict(list[PermissionParam])


def init_permissions():
    global PERMS, PERMS_MAP

    perms = getMenuPermissions()

    PERMS += perms

    for p in PERMS:
        if p.app == "":
            continue
        PERMS_MAP[p.app].append(p)
