from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from inventory.forms import TransactionCreateForm
from inventory.models import Product
from inventory.views.transaction import renderCreateTransaction
from services.tools.transaction import handle_transaction
from utils.models import Order


@login_required
def create_transaction(request, order_id, product_id):
    order = Order.objects.get(id=order_id)
    product = Product.objects.get(id=product_id)

    form = TransactionCreateForm(
        initial={"unit": product.unit, "price": product.getSuggestedPrice()},
        product=product,
        order=order,
    )
    if request.method == "POST":
        form = TransactionCreateForm(request.POST, product=product, order=order)
        if form.is_valid():
            with transaction.atomic():
                trans = form.save(commit=False)
                trans.order = order
                trans.product = product
                trans.save()
                if order.type == "sell":
                    if order.status != "pending" and order.status != "decline":
                        handle_transaction(trans)
                    return redirect("detail-service-order", id=order_id)
                if order.type == "purchase":
                    return redirect("detail-order", id=order_id)
    context = renderCreateTransaction(request, form, product, order_id)
    return render(request, "inventory/transaction_create.html", context)
