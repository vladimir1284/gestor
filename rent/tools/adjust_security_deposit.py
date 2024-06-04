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
            lease_deposits = []
            for lease in contract.lease_set.all():
                lease_deposits += lease.lease_deposit.all()

            dep_on_hold = False
            for dep in lease_deposits:
                if dep.on_hold:
                    dep_on_hold = True

            total_amount = sum([dep.amount for dep in lease_deposits])

            print(total_amount)
            if on_hold is not None and not dep_on_hold:
                total_amount += on_hold.amount
            print(total_amount)

            for dep in deposits:
                dep.delete()

            deposit = SecurityDepositDevolution.objects.create(
                contract=contract,
                total_deposited_amount=total_amount,
            )
        else:
            deposit = deposits.last()

    return contract, on_hold, deposit
