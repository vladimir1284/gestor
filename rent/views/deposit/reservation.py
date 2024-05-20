from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from rent.forms.trailer_deposit import TrailerDepositForm
from rent.forms.trailer_deposit import TrailerDepositTrace
from rent.models.lease import Associated
from rent.models.lease import Trailer
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.deposit import send_deposit_pdf
from rent.tools.get_conditions import get_on_hold_conditions_last_version
from rent.views.create_lessee_with_data import create_lessee
from rent.views.create_lessee_with_data import update_lessee


@login_required
def reserve_trailer(request, trailer_id):
    if request.method == "POST":
        lessee = get_object_or_404(Associated, id=request.POST.get("id"))
        return redirect("reserve-trailer-update-lessee", trailer_id, lessee.id)
        # return redirect("create-trailer-reservation", trailer_id, lessee.id)

    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "trailer_id": trailer_id,
        "create": True,
        "createUrl": reverse("reserve-trailer-create-lessee", args=[trailer_id]),
    }
    return render(request, "services/client_list.html", context)


@login_required
def update_lessee_for_reservation(request, trailer_id, lessee_id):
    return update_lessee(
        request,
        lessee_id,
        "create-trailer-reservation",
        [trailer_id, "{lessee_id}"],
        update_data=False,
    )


@login_required
def create_lessee_for_reservation(request, trailer_id):
    return create_lessee(
        request,
        "create-trailer-reservation",
        [trailer_id, "{lessee_id}"],
        use_client_url={
            "url": "reserve-trailer-update-lessee",
            "args": [
                trailer_id,
                "{client_id}",
            ],
        },
        update_data=False,
    )


@login_required
def create_trailer_reservation(request, trailer_id, lessee_id):
    if request.method == "POST":
        form = TrailerDepositForm(request.POST)
        if form.is_valid():
            with atomic():
                deposit: TrailerDeposit = form.save(commit=False)
                deposit.client = get_object_or_404(Associated, id=lessee_id)
                deposit.trailer = get_object_or_404(Trailer, id=trailer_id)
                deposit.template_version = get_on_hold_conditions_last_version()
                deposit.save()
                TrailerDepositTrace.objects.create(
                    status="created",
                    days=deposit.days,
                    amount=deposit.amount,
                    note=deposit.note,
                    trailer_deposit=deposit,
                )
                send_deposit_pdf(request, deposit)
                return redirect("trailer-deposit-details", deposit.id)
    else:
        form = TrailerDepositForm()
    context = {
        "form": form,
        "title": "Crear deposito",
    }
    return render(request, "rent/trailer_deposit_create.html", context)
