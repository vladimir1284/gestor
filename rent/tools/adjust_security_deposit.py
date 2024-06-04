from django.db import transaction
from django.shortcuts import get_object_or_404

from rent.models.lease import Contract
from rent.models.lease import SecurityDepositDevolution
from rent.models.trailer_deposit import TrailerDeposit


def adjust_security_deposit(contract_id, update: bool = False):
    contract: Contract = get_object_or_404(Contract, id=contract_id)
    on_hold = TrailerDeposit.objects.filter(done=True, contract=contract).last()

    deposits = SecurityDepositDevolution.objects.filter(contract=contract)
    with transaction.atomic():
        if deposits.count() != 1 or update:
            total_amount = sum(
                [
                    lease_deposit.amount
                    for lease in contract.lease_set.all()
                    for lease_deposit in lease.lease_deposit.all()
                ]
            )
            if on_hold is not None:
                total_amount += on_hold.amount

            for dep in deposits:
                dep.delete()

            deposit = SecurityDepositDevolution.objects.create(
                contract=contract,
                total_deposited_amount=total_amount,
            )
        else:
            deposit = deposits.last()

    return contract, on_hold, deposit
