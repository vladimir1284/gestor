import qrcode.image.svg
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from rent.forms.trailer_deposit import TrailerDepositForm
from rent.models.lease import Associated
from rent.models.lease import Trailer
from rent.models.trailer_deposit import TrailerDeposit
from rent.tools.deposit import send_deposit_pdf
from rent.tools.deposit import trailer_deposit_conditions_pdf
from rent.tools.deposit import trailer_deposit_context
from rent.views.vehicle import getImages


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
    deposit = get_object_or_404(TrailerDeposit, id=id)
    images, pinned_image = getImages(deposit.trailer)

    url_base = "{}://{}".format(request.scheme, request.get_host())
    url = url_base + reverse("trailer-deposit-conditions", args=[id])
    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=20,
    )

    context = {
        "deposit": deposit,
        "images": images,
        "pinned_image": pinned_image,
        "equipment": deposit.trailer,
        "qr_url": img.to_string(encoding="unicode"),
        "url": url,
    }
    return render(request, "rent/trailer_deposit_details.html", context)


def trailer_deposit_conditions(request, token):
    id = token
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
