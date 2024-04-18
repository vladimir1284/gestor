from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.debug import HttpRequest

from services.forms import OrderEndUpdatePositionForm
from utils.models import Order


def order_update_position(
    *,
    request: HttpRequest,
    id: int,
    status: str = "",
    next: str = "",
    args: list = [],
):
    order = get_object_or_404(Order, id=id)
    # if status == "decline":
    #     order.position = None
    #     order.save()
    #     return redirect("list-service-order")

    if status == "complete" and order.position is None:
        return redirect("process-payment", id)

    if request.method == "POST":
        form = OrderEndUpdatePositionForm(
            request.POST,
            order=order,
            status=status,
        )
        if form.is_valid():
            pos = form.cleaned_data["position"]
            reason = form.cleaned_data["reason"]
            if pos == "":
                pos = None
            order.position = pos
            order.storage_reason = reason
            order.save()
            if status == "complete":
                return redirect("process-payment", id)
            if next != "":
                return redirect(next, *args)
            return redirect("list-service-order")
    else:
        form = OrderEndUpdatePositionForm(order=order, status=status)

    context = {
        "form": form,
        "title": "Select position",
    }
    return render(request, "services/order_end_update_position.html", context)
