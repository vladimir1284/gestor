from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Contract
from rent.models.trailer_deposit import get_current_trailer_deposit
from rent.models.trailer_deposit import TrailerDeposit
from rent.models.vehicle import Trailer


def _resolver():
    ids = []

    active_contracts = Contract.objects.filter(stage__in=("active", "missing"))
    for contract in active_contracts:
        ids.append(contract.trailer.id)

    deposits = TrailerDeposit.objects.filter(cancelled=False, done=False)
    on_hold_trailers = []
    for dep in deposits:
        trailer = dep.trailer
        if trailer.id in ids:
            continue
        ids.append(trailer.id)
        trailer.on_hold = dep
        on_hold_trailers.append(trailer)

    active_trailers = Trailer.objects.filter(
        active=True,
    ).exclude(id__in=ids)

    return {
        "available": active_trailers,
        "on_hold": on_hold_trailers,
    }


def TrailersAvailableCard():
    return DashboardCard(
        name="Trailers available",
        template="dashboard/trailers_availables.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
