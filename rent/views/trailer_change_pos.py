from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.trailer_position import TrailerChangePosForm
from rent.models.vehicle import Trailer


def trailer_change_position(
    request: HttpRequest,
    id: int,
):
    trailer: Trailer = get_object_or_404(Trailer, id=id)

    if request.method == "POST":
        form = TrailerChangePosForm(
            request.POST,
            trailer=trailer,
        )
        if form.is_valid():
            pos = form.cleaned_data["position"]
            note = form.cleaned_data["note"]
            if pos == "":
                pos = None
            trailer.position = pos
            trailer.position_note = note
            trailer.position_date = datetime.now()
            trailer.save()
            # return redirect("list-service-order")
            return redirect("detail-trailer", id)
    else:
        form = TrailerChangePosForm(trailer=trailer)

    context = {
        "form": form,
        "title": "Select position",
    }
    return render(request, "services/order_end_update_position.html", context)
