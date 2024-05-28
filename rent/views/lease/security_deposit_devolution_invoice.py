from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from gestor.views.reports import get_object_or_404
from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import SecurityDepositDevolution


@login_required
def security_deposit_devolution_invoices(request: HttpRequest, id: int):
    dev: SecurityDepositDevolution = get_object_or_404(SecurityDepositDevolution, id=id)
    if dev.contract is not None:
        dis: DepositDiscount = get_object_or_404(DepositDiscount, contract=dev.contract)
    else:
        dis = None

    ctx = {
        "devolution": dev,
        "discount": dis,
    }
    return render(request, "rent/deposits/devolution_invoice.html", ctx)
