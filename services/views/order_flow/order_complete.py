from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from services.forms import OrderEndUpdatePositionForm
from utils.models import Order


@login_required
def order_complete(request: HttpRequest, id: int):
    order: Order = get_object_or_404(Order, id=id)

    posForm = OrderEndUpdatePositionForm(
        request.POST if request.method == "POST" else None,
        order=order,
        status="complete",
    )

    ctx = {
        "order": order,
        "posForm": posForm,
    }
    return render(request, "services/complete/view.html", ctx)
