from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Contract


def _resolver():
    contracts = Contract.objects.filter(stage="active")

    to_renew = []
    not_7 = 0
    unot_7 = 0
    not_15 = 0
    unot_15 = 0
    for c in contracts:
        if c.expirate_in_days <= 15:
            c.renovation = c.renovation_ctx
            to_renew.append(c)
            if c.expirate_in_days <= 7:
                if c.renovation_7_notify:
                    not_7 += 1
                else:
                    unot_7 += 1
            else:
                if c.renovation_15_notify:
                    not_15 += 1
                else:
                    unot_15 += 1

    to_renew.sort(key=lambda x: x.renovation["expirate_in_days"])

    return {
        "contracts": to_renew,
        "renov_not_7": not_7,
        "renov_not_15": not_15,
        "renov_unot_7": unot_7,
        "renov_unot_15": unot_15,
        "renov_not": not_7 + not_15,
        "renov_unot": unot_7 + unot_15,
    }


def ContractRenovationCard():
    return DashboardCard(
        name="Contract Renovations",
        template="dashboard/contract_renovation.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
