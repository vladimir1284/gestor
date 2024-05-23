from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rent.forms.deposit_discount import DepositDiscountForm
from rent.forms.lease import SecurityDepositDevolutionForm
from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import LeaseDocument
from rent.models.lease import SecurityDepositDevolution
from rent.tools.adjust_security_deposit import adjust_security_deposit
from rent.views.lease.deposit_discount import get_deposit_discount
from rent.views.vehicle import FILES_ICONS


@login_required
@atomic
def adjust_end_deposit(request, id):
    closing = request.GET.get("closing", False)
    contract, on_hold, deposit = adjust_security_deposit(id)
    discount: DepositDiscount = get_deposit_discount(contract)

    if (
        contract.stage == "missing"
        and deposit.total_deposited_amount == 0
        and (on_hold is None or on_hold.amount == 0)
    ):
        return redirect("update-contract-stage", id, "ended")
    elif contract.stage == "missing":
        return redirect("adjust-deposit-on-hold-from-contract", id)

    if request.method == "POST":
        form = SecurityDepositDevolutionForm(request.POST, instance=deposit)
        formDiscount = DepositDiscountForm(request.POST, instance=discount)
        if form.is_valid() and formDiscount.is_valid():
            instance: SecurityDepositDevolution = form.save(commit=False)
            discount: DepositDiscount = formDiscount.save()

            if instance.immediate_refund:
                instance.returned = True

            if instance.returned:
                instance.returned_date = timezone.now().date()
            else:
                instance.returned_date = None

            instance.amount = instance.total_deposited_amount - discount.total_discount
            instance.save()

            if closing:
                return redirect("update-contract-stage", id, "ended")
            else:
                return redirect("client-list")
    else:
        form = SecurityDepositDevolutionForm(instance=deposit)
        formDiscount = DepositDiscountForm(instance=discount)

    documents = LeaseDocument.objects.filter(contract=contract)
    for doc in documents:
        doc.icon = "assets/img/icons/" + FILES_ICONS[doc.document_type]
    context = {
        "title": "Adjust Security Deposit devolution.",
        "form": form,
        "initial": deposit.total_deposited_amount,
        "on_contract": deposit.contract.security_deposit,
        "documents": documents,
        "contract": contract,
        "discount": discount,
        "formDiscount": formDiscount,
    }
    return render(request, "rent/contract/adjust_deposit.html", context)
