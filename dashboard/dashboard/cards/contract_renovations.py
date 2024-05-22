from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Contract


def _resolver():
    contracts = Contract.objects.filter(stage="active")

    to_renew = []
    for c in contracts:
        if c.expirate_in_days <= 15:
            c.renovation = c.renovation_ctx
            to_renew.append(c)

    to_renew.sort(key=lambda x: x.renovation["expirate_in_days"])

    return {
        "contracts": to_renew,
    }


def ContractRenovationCard():
    return DashboardCard(
        name="Contract Renovations",
        template="dashboard/contract_renovation.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
