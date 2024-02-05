from rent.models.lease import Contract
from users.models import Associated


def get_lessee() -> list[Associated]:
    contracts = Contract.objects.filter(stage="active").order_by(
        "lessee__name", "lessee__alias"
    )
    clients = []
    for contract in contracts:
        client = contract.lessee
        if client not in clients:
            clients.append(client)
    return clients
