from killbill.tools.get_contracts import get_contracts
from rent.models.lease import Lease


def get_leases() -> list[Lease]:
    contracts = get_contracts()
    return Lease.objects.filter(contract__in=contracts)
