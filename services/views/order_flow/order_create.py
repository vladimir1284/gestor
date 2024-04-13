from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from services.forms import OrderCreateForm
from services.models import Order
from services.models.preorder import Preorder
from services.tools.conditios_to_pdf import send_pdf_conditions_to_email


@login_required
def create_order(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)

    # if signature is required
    # but there is not any signature
    # and there is a client with not any previous order
    # redirect him to view_conditions
    if (
        preorder.using_signature
        and preorder.signature is None
        and preorder.associated is not None
        # and not Order.objects.filter(associated=preorder.associated).exists()
    ):
        return redirect("view-conditions", id)

    initial = {
        "concept": preorder.concept,
    }
    request.session["all_selected"] = True
    order = Order()
    if preorder.creating_order:
        order.associated = preorder.associated
        order.company = preorder.company
        order.trailer = preorder.trailer
        initial["concept"] = preorder.concept

    if request.method == "POST":
        form = OrderCreateForm(request.POST, get_plate=preorder.external)
        form.clean()
        if form.is_valid():
            order = form.save(commit=False)
            order.type = "sell"
            order.created_by = request.user

            # Link the client to order
            order.associated = preorder.associated

            # Set the equipment type in the order
            order.equipment_type = preorder.equipment_type

            # Link trailer to order if exists
            order.trailer = preorder.trailer

            # Link company to order if exists
            order.company = preorder.company

            order.save()

            preorder.order = order
            preorder.completed = True
            preorder.save()

            if order.associated is not None and order.associated.email is not None:
                send_pdf_conditions_to_email(
                    request, order.id, [order.associated.email]
                )

            return redirect("detail-service-order", id=order.id)
    else:
        form = OrderCreateForm(initial=initial, get_plate=preorder.external)

    context = {
        "form": form,
        "title": _("Create service order"),
        "order": order,
    }
    return render(request, "services/order_create.html", context)
