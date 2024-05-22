from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from rent.models.lease import Contract


@login_required
def notify_contract_renovation(request: HttpRequest, id: int):
    contract: Contract = get_object_or_404(Contract, id=id)
    contract.notify()

    return redirect("dashboard")
