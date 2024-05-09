import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from rent.forms.lease import AssociatedCreateForm
from rent.forms.lease import LesseeDataForm
from rent.forms.trailer_deposit import TrailerDepositForm
from rent.forms.trailer_deposit import TrailerDepositRenovationForm
from rent.forms.trailer_deposit import TrailerDepositTrace
from rent.models.lease import Associated
from rent.models.lease import LesseeData
from rent.models.lease import Trailer
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.deposit import send_deposit_pdf
from rent.tools.deposit import trailer_deposit_conditions_pdf
from rent.tools.deposit import trailer_deposit_context
from rent.views.create_lessee_with_data import create_lessee
from rent.views.create_lessee_with_data import create_lessee_with_data
from rent.views.create_lessee_with_data import update_lessee
from rent.views.create_lessee_with_data import update_lessee_with_data
from rent.views.lease import addStateCity


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
        [trailer_id, lessee_id],
    )


@login_required
def create_lessee_for_reservation(request, trailer_id):
    return create_lessee(
        request,
        "create-trailer-reservation",
        [trailer_id, "{lessee_id}"],
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

    form = TrailerDepositForm()
    context = {
        "form": form,
        "title": "Crear deposito",
    }
    return render(request, "rent/trailer_deposit_create.html", context)


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


@login_required
def trailer_deposit_details(request, id):
    context = trailer_deposit_context(request, id)
    return render(request, "rent/trailer_deposit_details.html", context)


def trailer_deposit_conditions(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        id = info["deposit_id"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)

    context = trailer_deposit_context(request, id)
    return render(request, "rent/trailer_deposit_conditions.html", context)


def trailer_deposit_pdf(request, id):
    result = trailer_deposit_conditions_pdf(request, id)
    if result is not None:
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        response.status_code = 200
        response.write(result)
        return response
    return None
