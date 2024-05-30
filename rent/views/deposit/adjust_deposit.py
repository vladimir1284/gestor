from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.timezone import datetime

from rent.forms.trailer_deposit import OnHoldDepositDevolutionForm
from rent.models.lease import Contract
from rent.models.lease import SecurityDepositDevolution
from rent.models.trailer_deposit import TrailerDeposit


@login_required
@atomic
def adjust_deposit_on_hold_from_contract(request, id):
    contract: Contract = get_object_or_404(Contract, id=id)
    deposit, c = SecurityDepositDevolution.objects.get_or_create(contract=contract)
    on_hold = TrailerDeposit.objects.filter(done=True, contract=contract).last()

    if (
        contract.stage == "missing"
        and (c or deposit.total_deposited_amount == 0)
        and (on_hold is None or on_hold.amount == 0)
    ):
        return redirect("update-contract-stage", id, "ended")

    if c:
        total_amount = sum(
            [
                lease_deposit.amount
                for lease in contract.lease_set.all()
                for lease_deposit in lease.lease_deposit.all()
            ]
        )
        if on_hold is not None:
            total_amount += on_hold.amount

        deposit.total_deposited_amount = total_amount
        deposit.save()

    if request.method == "POST":
        form = OnHoldDepositDevolutionForm(request.POST, instance=deposit)
        if form.is_valid():
            instance: SecurityDepositDevolution = form.save(commit=False)
            instance.returned = True
            instance.returned_date = datetime.now().date()
            instance.save()

            on_hold.cancelled = True
            on_hold.done = True
            on_hold.returned_amount = instance.amount
            on_hold.save()

            return redirect("update-contract-stage", id, "ended")
    else:
        form = OnHoldDepositDevolutionForm(instance=deposit)

    context = {
        "title": "On Hold Deposit devolution.",
        "form": form,
        "initial": deposit.total_deposited_amount,
        "on_contract": deposit.contract.security_deposit,
        "contract": contract,
    }
    return render(request, "rent/contract/adjust_deposit_on_hold.html", context)
