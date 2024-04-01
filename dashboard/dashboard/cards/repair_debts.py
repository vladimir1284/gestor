from dashboard.dashboard.dashboard_card import DashboardCard
from users.views import get_debtor


def _resolver(request):
    return get_debtor(request)


def RepairDebtsCard():
    return DashboardCard(
        template="dashboard/repair_debt.html",
        resolver=_resolver,
    )
