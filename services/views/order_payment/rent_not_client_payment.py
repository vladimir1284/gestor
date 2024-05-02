from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone

from gestor.tools.set_not import set_not
from services.models import Order
from services.models.towit_payment import TowitPayment
from services.tools.order import getOrderContext
from services.tools.sms import twilioSendSMS
from services.tools.transaction import handle_order_transactions


@login_required()
@atomic()
def process_payment_rent_without_client(request, order_id, decline_unsatisfied=False):
    order: Order = get_object_or_404(Order, id=order_id)
    context = getOrderContext(order_id)
    total = context["order"].total
    payment = TowitPayment(
        amount=total,
        order=order,
        note="Trailer maintenance",
    )
    payment.save()

    handle_order_transactions(order, decline_unsatisfied=decline_unsatisfied)
    order.terminated_date = timezone.now()
    order.terminated_user = request.user
    order.status = "complete"
    order.save()
    twilioSendSMS(order, order.status)

    set_not(
        request,
        title="Success",
        msg=f"TowitHouston Rent debts to TowitHouston Services {total}",
        icon="bx-money",
    )
    return redirect("detail-service-order", order_id)
