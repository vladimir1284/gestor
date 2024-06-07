from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _

from rent.models.lease import SecurityDepositDevolution


@login_required
@atomic
def return_security_deposit(request: HttpRequest, id: int):
    devolution: SecurityDepositDevolution = get_object_or_404(
        SecurityDepositDevolution,
        id=id,
    )

    devolution.returned_date = datetime.now()
    devolution.returned = True
    devolution.save()

    return redirect("ended-contract-details", devolution.contract.id)
