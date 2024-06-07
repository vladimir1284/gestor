from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import Contract
from rent.models.lease import Due
from rent.models.lease import SecurityDepositDevolution
from tolls.models import TollDue


@login_required
def ended_contract_details(request: HttpRequest, id: int):
    contract: Contract = get_object_or_404(Contract, id=id)
    devolution = SecurityDepositDevolution.objects.filter(contract=contract).last()
    discount = DepositDiscount.objects.filter(contract=contract).last()
    renovations = contract.renovation_ctx

    # TODO include dues in template
    dues = Due.objects.filter(contract=contract).order_by("-due_date")
    dues_total = sum([d.amount for d in dues])

    unpaid_dues = [] if discount is None else discount.unpaid_dues_list
    unpaid_total = sum([u.amount for u in unpaid_dues])

    # TODO include tolls in template
    tolls_paid = TollDue.objects.filter(contract=contract, stage="paid")
    tolls_unpaid = TollDue.objects.filter(contract=contract).exclude(stage="paid")
    tolls_paid_total = sum([t.amount for t in tolls_paid])
    tolls_unpaid_total = sum([t.amount for t in tolls_unpaid])

    ctx = {
        # Contract dev and dis
        "contract": contract,
        "devolution": devolution,
        "discount": discount,
        # Payments and debts
        "dues": dues,
        "dues_total": dues_total,
        "unpaid_dues": unpaid_dues,
        "unpaid_total": unpaid_total,
        # Tolls
        "tolls_paid": tolls_paid,
        "tolls_unpaid": tolls_unpaid,
        "tolls_paid_total": tolls_paid_total,
        "tolls_unpaid_total": tolls_unpaid_total,
        # Renovations
        "renovations": [
            r
            for r in renovations["renovations"]
            if r.effective_date <= discount.expiration_date
        ],
    }
    return render(
        request, "rent/contract/ended_contract/ended_contract_details.html", ctx
    )
