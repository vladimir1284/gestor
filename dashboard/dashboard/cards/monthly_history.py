from dashboard.dashboard.dashboard_card import DashboardCard
from dashboard.tools.get_indicators import get_indicators
from rbac.tools.permission_param import PermissionParam


def _resolver():
    print("monthly history")
    return {
        "indicators": get_indicators(),
    }


def MonthlyHistoryCard():
    return DashboardCard(
        name="Monthly history",
        template="dashboard/monthly_history.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
