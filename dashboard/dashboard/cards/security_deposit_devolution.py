from django.utils.timezone import datetime

from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import SecurityDepositDevolution
from rent.tools.security_deposit_reports import security_deposit_reports


def _resolver():
    ctx = {}
    security_deposit_reports(ctx)

    now = datetime.now().date()

    security_pendings: list[SecurityDepositDevolution] = ctx["security_pending"]
    return_now = [dep for dep in security_pendings if dep.refund_date <= now]
    return_later = [dep for dep in security_pendings if dep.refund_date > now]

    return {
        "return_now": return_now,
        "return_later": return_later,
    }


def SecurityDepositDevPendingCard():
    return DashboardCard(
        name="Pending Security Devolution",
        template="dashboard/security_deposit_devolution.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
