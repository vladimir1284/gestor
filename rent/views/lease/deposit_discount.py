from datetime import datetime

from django.db.transaction import atomic
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.deposit_discount import DepositDiscountForm
from rent.models.deposit_discount import DepositDiscount
from rent.tools.adjust_security_deposit import adjust_security_deposit
from rent.tools.get_conditions import relativedelta


@atomic
def deposit_discount(request: HttpRequest, contract_id: int):
    contract, on_hold, deposit = adjust_security_deposit(contract_id)
    discount, _ = DepositDiscount.objects.get_or_create(contract=contract)

    eff_date = contract.effective_date
    end_date = eff_date + relativedelta(months=contract.contract_term)
    rem_days = (datetime.now().date() - end_date).days

    discount.duration = rem_days
    discount.save()

    if request.method == "POST":
        form = DepositDiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            return redirect("adjust-deposit", contract_id)
    else:
        form = DepositDiscountForm(instance=discount)

    ctx = {
        "title": "Check contract conditions",
        "form": form,
    }
    return render(request, "rent/contract/discount/deposit_discount.html", ctx)
