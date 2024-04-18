from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from services.forms import OrderDeclineReazon
from services.forms import OrderDeclineReazonForm
from services.views.category import login_required
from services.views.expense import render
from utils.models import Order


@login_required
def order_decline_reazon(request: HttpRequest, id):
    order = get_object_or_404(Order, id=id)
    decline_reazon = OrderDeclineReazon.objects.filter(order=order).first()

    if request.method == "POST":
        form = OrderDeclineReazonForm(
            request.POST,
            instance=decline_reazon,
        )
        if form.is_valid():
            decline_reazon = form.save(commit=False)
            decline_reazon.order = order
            decline_reazon.save()
            return redirect("update-service-order-status", order.id, "decline")
    else:
        form = OrderDeclineReazonForm(instance=decline_reazon)

    context = {
        "form": form,
        "title": "Decline reazon",
    }
    return render(request, "services/order_end_update_position.html", context)
