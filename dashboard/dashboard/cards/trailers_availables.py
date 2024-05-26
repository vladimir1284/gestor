from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Contract
from rent.models.trailer_deposit import get_current_trailer_deposit
from rent.models.trailer_deposit import TrailerDeposit
from rent.models.vehicle import Trailer


def _resolver():
    active_trailers = []
    on_hold_trailers = []

    trailers = Trailer.objects.filter(active=True)
    for trailer in trailers:
        # Contracts
        contract = (
            Contract.objects.filter(trailer=trailer)
            .exclude(stage__in=("ended", "garbage"))
            .last()
        )
        if contract and contract.stage == "active":
            continue

        trailer.current_contract = contract
        is_on_hold = False
        if contract:
            trailer_deposit = TrailerDeposit.objects.filter(
                contract=contract,
                trailer=trailer,
                cancelled=False,
            )
            if trailer_deposit:
                trailer.on_hold = trailer_deposit
                is_on_hold = True
        else:
            trailer_deposits = get_current_trailer_deposit(trailer)
            if trailer_deposits:
                trailer.on_hold = trailer_deposits
                is_on_hold = True
        if is_on_hold:
            on_hold_trailers.append(trailer)
        else:
            active_trailers.append(trailer)

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
