from dashboard.dashboard.dashboard import DASHBOARD
from rbac.tools.permission_param import PermissionParam


def get_dashboard_cards_perms() -> list[PermissionParam]:
    perms: list[PermissionParam] = []
    for dc in DASHBOARD:
        perm = dc.self_perm
        if perm is not None:
            perms.append(perm)

    return perms
