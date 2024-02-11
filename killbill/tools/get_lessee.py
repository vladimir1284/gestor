from killbill.tools.get_contracts import get_contracts
from users.models import Associated


def get_lessee() -> list[Associated]:
    contracts = get_contracts()
    clients = []
    for contract in contracts:
        client = contract.lessee
        if client not in clients:
            clients.append(client)
    return clients
