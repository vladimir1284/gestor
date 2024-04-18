import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.models import Order
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder
from services.tools.get_order_conditions import get_order_conditions


def contact_view_conditions(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        preorder_id = info["preorder"]
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

    preorder: Preorder = get_object_or_404(Preorder, id=preorder_id)
    preorder.new_associated = False
    preorder.save()

    if request.method == "POST":
        preorder.completed = False
        preorder.save()
        return redirect("process-ended-page")

    old_sign = (
        OrderSignature.objects.filter(associated=preorder.associated).last()
        if preorder.associated is not None and preorder.signature is None
        else None
    )
    signature = preorder.signature

    HasOrders = (
        Order.objects.filter(associated=preorder.associated).exists()
        if preorder.associated is not None
        else False
    )

    context = {
        "signature": signature,
        "old_sign": old_sign,
        "client": preorder.associated,
        "hasOrder": HasOrders,
        "token": token,
    }
    context["conditions"] = get_order_conditions(preorder, context)
    return render(request, "services/contact_view_conditions.html", context)
