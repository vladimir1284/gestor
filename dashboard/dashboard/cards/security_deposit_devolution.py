from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.tools.security_deposit_reports import security_deposit_reports


def _resolver():
    ctx = {}
    security_deposit_reports(ctx)

    return ctx


def SecurityDepositDevPendingCard():
    return DashboardCard(
        name="Pending Security Devolution",
        template="dashboard/security_deposit_devolution.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
