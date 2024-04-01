from dashboard.dashboard.dashboard_card import DashboardCard
from rent.models.lease import Contract
from rent.models.trailer_deposit import get_current_trailer_deposit
from rent.models.vehicle import Trailer


def _resolver():
    active_contracts = Contract.objects.filter(stage__in=("active", "missing"))
    rented_ids = []
    for contract in active_contracts:
        rented_ids.append(contract.trailer.id)

    active_trailers = Trailer.objects.filter(
        active=True).exclude(id__in=rented_ids)
    available = []
    for t in active_trailers:
        if get_current_trailer_deposit(t) is None:
            available.append(t)
    return {
        "available": available,
    }


def TrailersAvailableCard():
    return DashboardCard(
        template="dashboard/trailers_availables.html",
        resolver=_resolver,
    )
