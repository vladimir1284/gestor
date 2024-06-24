from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from inventory.views.transaction import getTransactionAmount
from services.forms import TransactionCreateForm
from services.models import Order
from services.models import Service
from services.models import ServiceTransaction

# -------------------- Transaction ----------------------------


def renderCreateTransaction(request, form, service, order_id):
    context = {
        "form": form,
        "service": service,
        "order_id": order_id,
        "title": _("Add service"),
        "create": True,
    }
    return render(request, "services/transaction_create.html", context)


@login_required
def create_transaction(request, order_id, service_id):
    order = Order.objects.get(id=order_id)
    service = Service.objects.get(id=service_id)
    initial = {"price": service.suggested_price}
    form = TransactionCreateForm(initial=initial)
    if request.method == "POST":
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.service = service
            trans.save()
            return redirect("detail-service-order", id=order_id)
    return renderCreateTransaction(request, form, service, order_id)


@login_required
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(request.POST or None, instance=transaction)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect("detail-service-order", id=transaction.order.id)

    # add form dictionary to context
    context = {
        "form": form,
        "service": transaction.service,
        "order_id": transaction.order.id,
        "title": _("Update Transaction"),
        "create": False,
    }

    return render(request, "services/transaction_create.html", context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)
    return render(
        request,
        "services/transaction_detail.html",
        {"transaction": transaction, "amount": getTransactionAmount(transaction)},
    )


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)
    transaction.delete()
    return redirect("detail-service-order", id=transaction.order.id)
