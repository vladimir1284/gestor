from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.forms import OrderEndUpdatePositionForm
from services.tools.order import getOrderContext
from utils.models import Order


@login_required
def order_complete(request: HttpRequest, id: int):
    order: Order = get_object_or_404(Order, id=id)

    otype = ""
    if order.external:
        otype = "external"
    elif order.rent_with_client:
        otype = "client"
    elif order.rent_without_client:
        otype = "rent"

    request.session["new_position"] = None
    request.session["new_position_reason"] = None

    form = OrderEndUpdatePositionForm(
        request.POST if request.method == "POST" else None,
        order=order,
        status="complete",
    )

    flow = (
        request.POST["flow"]
        if request.method == "POST" and "flow" in request.POST
        else ""
    )

    errs = []
    if flow != "" and request.method == "POST":
        if form.is_valid():
            pos = form.cleaned_data["position"]
            reason = form.cleaned_data["reason"]
            if pos == "":
                pos = None

            if flow == "processPay" and not order.rent_without_client:
                request.session["new_position"] = pos if pos is not None else -1
                request.session["new_position_reason"] = reason
                return redirect("process-payment", id)

            order.position = pos
            order.storage_reason = reason
            order.save()

            if flow == "processPay":
                # if order.rent_without_client:
                #     return redirect("service-order-payment-trailer-without-client", id)
                # return redirect("process-payment", id)
                return redirect("service-order-payment-trailer-without-client", id)

            if flow == "pendingPay":
                if pos is not None:
                    return redirect(
                        "update-service-order-status", id, "payment_pending"
                    )
                errs.append("Pending payment trailer can go outside.")

    context = getOrderContext(id)
    total = context["order"].total
    ctx = {
        "order": order,
        "posForm": form,
        "orderType": otype,
        "total": total,
        "errs": errs,
    }
    return render(request, "services/complete/view.html", ctx)
