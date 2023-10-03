from rent.models.lease import Lease, Contract
from rent.views.client import compute_client_debt
from django.utils import timezone

# Get all clients with debt
contracts = Contract.objects.exclude(stage="ended")
clients = []
for contract in contracts:
    client = contract.lessee
    if contract.stage == "active":
        try:
            lease = Lease.objects.get(contract=contract)
        except Lease.DoesNotExist:
            lease = Lease.objects.create(
                contract=contract,
                payment_amount=contract.payment_amount,
                payment_frequency=contract.payment_frequency,
                event=None,
            )
        debt, last_payment, unpaid_dues = compute_client_debt(
            client, lease)
        if len(unpaid_dues) > 0:
            client.debt = debt
            client.lease = lease
            client.last_payment = last_payment
            client.unpaid_dues = unpaid_dues
            clients.append(client)

# Process the alarms
for client in clients:
    print("==================")
    print("Client Name:", client.name)
    print("Debt:", client.debt)
    print("Last Payment:", client.last_payment)
    print("Unpaid Dues:", client.unpaid_dues)
    print()
