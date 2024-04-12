from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.models import Order
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder
from services.tools.get_order_conditions import get_order_conditions


@login_required
def view_conditions(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)

    if request.method == "POST" or preorder.signature is not None:
        preorder.new_associated = False
        preorder.save()
        return redirect("create-service-order", id)

    old_sign = (
        OrderSignature.objects.filter(associated=preorder.associated).last()
        if preorder.associated is not None
        else None
    )

    signature = OrderSignature()

    HasOrders = (
        Order.objects.filter(
            associated=preorder.associated,
        ).exists()
        if preorder.associated is not None
        else False
    )

    context = {
        "signature": signature,
        "client": preorder.associated,
        "hasOrder": HasOrders,
        "preorder": id,
        "old_sign": old_sign,
    }
    context["conditions"] = get_order_conditions(preorder, context)
    return render(request, "services/view_conditions.html", context)
