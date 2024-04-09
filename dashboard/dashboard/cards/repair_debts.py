from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from users.views import get_debtor


def _resolver(request):
    return get_debtor(request)


def RepairDebtsCard():
    return DashboardCard(
        name="Repair debt",
        template="dashboard/repair_debt.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
