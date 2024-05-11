from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.trailer_deposit import TrailerDepositRenovationForm
from rent.forms.trailer_deposit import TrailerDepositTrace
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.deposit import send_deposit_pdf


@login_required
def renovate_trailer_reservation(request, deposit_id):
    deposit: TrailerDeposit = get_object_or_404(TrailerDeposit, id=deposit_id)

    if request.method == "POST":
        form = TrailerDepositRenovationForm(request.POST)
        if form.is_valid():
            with atomic():
                renovation: TrailerDepositTrace = form.save(commit=False)
                renovation.status = "renovated"
                renovation.trailer_deposit = deposit
                renovation.save()
                deposit.days = deposit.days + renovation.days
                deposit.save()
                send_deposit_pdf(request, deposit)
                return redirect("trailer-deposit-details", deposit.id)

    form = TrailerDepositRenovationForm()
    context = {
        "form": form,
        "title": "Renovate deposit",
    }
    return render(request, "rent/trailer_deposit_create.html", context)


@login_required
@atomic
def trailer_deposit_cancel(request, id):
    deposit: TrailerDeposit = get_object_or_404(TrailerDeposit, id=id)
    deposit.cancelled = True
    deposit.save()
    TrailerDepositTrace.objects.create(
        status="finished",
        days=0,
        amount=0,
        trailer_deposit=deposit,
    )

    return redirect("trailer-deposit-details", id)
