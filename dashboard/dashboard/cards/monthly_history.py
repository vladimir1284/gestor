from dashboard.dashboard.dashboard_card import DashboardCard
from dashboard.tools.get_indicators import get_indicators


def _resolver():
    return {
        "indicators": get_indicators(),
    }


def MonthlyHistoryCard():
    return DashboardCard(
        template="dashboard/monthly_history.html",
        resolver=_resolver,
    )
