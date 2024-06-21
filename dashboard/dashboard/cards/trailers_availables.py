from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Contract
from rent.models.trailer_deposit import get_current_trailer_deposit
from rent.models.trailer_deposit import TrailerDeposit
from rent.models.vehicle import Trailer


def _resolver():
    print("Trailer availables")
    active_trailers = []
    on_hold_trailers = []

    trailers = (
        Trailer.objects.filter(active=True)
        .select_related(
            "manufacturer",
        )
        .prefetch_related(
            "trailer_deposit",
            "trailer_deposit__contract",
        )
    )

    contracts = Contract.objects.select_related(
        "trailer",
    ).exclude(
        stage__in=("ended", "garbage"),
    )
    contracts_map = {}
    for contract in contracts:
        contracts_map[contract.trailer.id] = contract

    for trailer in trailers:
        # Contracts
        # contract = (
        #     Contract.objects.filter(trailer=trailer)
        #     .exclude(stage__in=("ended", "garbage"))
        #     .last()
        # )
        contract = contracts_map[trailer.id] if trailer.id in contracts_map else None
        if contract and contract.stage == "active":
            continue

        trailer.current_contract = contract
        is_on_hold = False
        if contract:
            trailer_deposits = [
                td
                for td in trailer.trailer_deposit.all()
                if td.contract is not None
                and td.contract.id == contract.id
                and td.cancelled is False
            ]
            if len(trailer_deposits) > 0:
                trailer.on_hold = trailer_deposits[-1]
                is_on_hold = True
        else:
            trailer_deposits = [
                td
                for td in trailer.trailer_deposit.all()
                if td.done is False and td.cancelled is False
            ]
            if len(trailer_deposits) > 0:
                trailer.on_hold = trailer_deposits[-1]
                is_on_hold = True
            # trailer_deposit = trailer.trailer_deposit.filter(
            #     done=False,
            #     cancelled=False,
            # ).last()
            # # trailer_deposit = get_current_trailer_deposit(trailer)
            # if trailer_deposit:
            #     trailer.on_hold = trailer_deposit
            #     is_on_hold = True
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
