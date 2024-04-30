from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone

from gestor.tools.set_not import set_not
from inventory.models import (
    ProductTransaction,
)
from services.models import Order
from services.models.towit_payment import TowitPayment
from services.tools.order import getOrderContext
from services.tools.sms import twilioSendSMS
from services.tools.transaction import handle_transaction


@login_required()
@atomic()
def process_payment_rent_without_client(request, order_id):
    # debt, created = PaymentCategory.objects.get_or_create(
    #     name="debt", defaults={"name": "debt", "icon": "assets/img/icons/debt.png"}
    # )

    order: Order = get_object_or_404(Order, id=order_id)
    context = getOrderContext(order_id)
    total = context["order"].total
    # category: PaymentCategory = debt
    # payment = Payment(
    #     amount=total,
    #     order=order,
    #     category=category,
    #     extra_charge=category.extra_charge,
    # )
    payment = TowitPayment(
        amount=total,
        order=order,
        note="Trailer maintenance",
    )
    payment.save()

    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        handle_transaction(transaction)
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
