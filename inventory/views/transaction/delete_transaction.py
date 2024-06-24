from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from inventory.models import ProductTransaction
from services.tools.transaction import reverse_transaction


@login_required
@atomic
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction: ProductTransaction = get_object_or_404(ProductTransaction, id=id)
    if transaction.order.type == "sell":
        if (
            transaction.order.status != "pending"
            and transaction.order.status != "decline"
        ):
            reverse_transaction(transaction)
        transaction.delete()  # must be after reverse_transaction
        return redirect("detail-service-order", id=transaction.order_id)

    if transaction.order.type == "purchase":
        transaction.delete()
        return redirect("detail-order", id=transaction.order_id)
