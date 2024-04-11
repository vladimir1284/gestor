from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.models import Order
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder
from services.models.preorder_data import PreorderData
from services.tools.get_order_conditions import get_order_conditions


@login_required
def view_conditions(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)
    if request.method == "POST" or (
        preorder.preorder_data is not None
        and preorder.preorder_data.signature is not None
    ):
        return redirect("create-service-order", id)

    if preorder.preorder_data is None:
        preorder_data = PreorderData()
        preorder_data.save()
        preorder.preorder_data = preorder_data
        preorder.save()

    signature = OrderSignature()

    HasOrders = (
        Order.objects.filter(
            associated=preorder.preorder_data.associated,
        ).exists()
        if preorder.preorder_data is not None
        and preorder.preorder_data.associated is not None
        else False
    )

    context = {
        "signature": signature,
        "client": preorder.preorder_data.associated,
        "hasOrder": HasOrders,
        "preorder": id,
        "conditions": get_order_conditions(preorder),
    }
    return render(request, "services/view_conditions.html", context)
