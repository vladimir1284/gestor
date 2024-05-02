from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from inventory.tools.transaction import NotEnoughStockError
from services.models import Order
from services.tools.transaction import check_order_transactions
from services.tools.transaction import decline_order_transaction
from services.tools.transaction import handle_order_transactions
from services.tools.transaction import reverse_order_transactions
from services.views.sms import twilioSendSMS


@login_required
def update_order_status(request, id, status):
    order: Order = get_object_or_404(Order, id=id)

    try:
        with transaction.atomic():
            if status == "complete":
                if not check_order_transactions(order):
                    return redirect(
                        "detail-service-order",
                        id,
                        "This order is not satisfied",
                    )
                return redirect("update-order-position", id, status)

            elif status == "decline":
                if order.status != "pending" and order.status != "decline":
                    # Reverse stock
                    reverse_order_transactions(order)
                    # transactions = ProductTransaction.objects.filter(order=order)
                    # for transaction in transactions:
                    #     reverse_transaction(transaction)

            elif status == "processing":
                if (
                    order.status == "pending"
                    and not order.company
                    and not order.associated
                ):
                    return redirect(
                        "detail-service-order",
                        id,
                        "Please add a client or a company",
                    )
                # process stock
                handle_order_transactions(order)

                order.processing_date = timezone.localtime(timezone.now())
                order.processing_user = request.user
                # Send SMS
                twilioSendSMS(order, status)

            order.status = status
            order.save()
    except NotEnoughStockError as error:
        print(error)

    if status == "processing":
        return redirect("service-labor", id)
    if status == "decline":
        return redirect("update-order-position", id, status)
    return redirect("list-service-order")
