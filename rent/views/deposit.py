import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.trailer_deposit import TrailerDepositForm
from rent.models.lease import Associated
from rent.models.lease import Trailer
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.deposit import send_deposit_pdf
from rent.tools.deposit import trailer_deposit_conditions_pdf
from rent.tools.deposit import trailer_deposit_context


@login_required
def reserve_trailer(request, trailer_id):
    if request.method == "POST":
        lessee = get_object_or_404(Associated, id=request.POST.get("id"))
        return redirect("create-trailer-reservation", trailer_id, lessee.id)

    # add form dictionary to context
    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "trailer_id": trailer_id,
        "create": True,
    }
    return render(request, "services/client_list.html", context)


@login_required
def create_trailer_reservation(request, trailer_id, lessee_id):
    if request.method == "POST":
        form = TrailerDepositForm(request.POST)
        if form.is_valid():
            deposit: TrailerDeposit = form.save(commit=False)
            deposit.client = get_object_or_404(Associated, id=lessee_id)
            deposit.trailer = get_object_or_404(Trailer, id=trailer_id)
            deposit.save()
            send_deposit_pdf(request, deposit)
            return redirect("trailer-deposit-details", deposit.id)

    form = TrailerDepositForm()
    context = {
        "form": form,
        "title": "Crear deposito",
    }
    return render(request, "rent/trailer_deposit_create.html", context)


@login_required
def trailer_deposit_cancel(request, id):
    deposit: TrailerDeposit = get_object_or_404(TrailerDeposit, id=id)
    deposit.cancelled = True
    deposit.save()

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
