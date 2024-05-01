from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from inventory.forms import TransactionCreateForm
from inventory.models import ProductTransaction
from inventory.tools.transaction import renderCreateTransaction
from services.tools.transaction import handle_transaction
from services.tools.transaction import reverse_transaction
from utils.models import Order


@login_required
@atomic
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ProductTransaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(
        request.POST or None,
        instance=transaction,
        id=transaction.id,
        product=transaction.product,
        order=transaction.order,
    )

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        order: Order = transaction.order
        if order.type == "sell":
            if order.status != "pending" and order.status != "decline":
                old_trans = get_object_or_404(ProductTransaction, id=id)
                reverse_transaction(old_trans)

            transaction = form.save()

            if order.status != "pending" and order.status != "decline":
                handle_transaction(transaction)

            return redirect("detail-service-order", id=transaction.order.id)

        if order.type == "purchase":
            form.save()
            return redirect("detail-order", id=transaction.order.id)

    # add form dictionary to context
    context = renderCreateTransaction(
        request, form, transaction.product, transaction.order.id
    )
    context["title"] = _("Update Transaction")
    context["create"] = False
    return render(request, "inventory/transaction_create.html", context)
