import os
from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    HttpResponseRedirect)
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

from users.models import (
    Associated,
)

from inventory.views import (
    convertUnit,
    getTransactionAmount,
    DifferentMagnitudeUnitsError,
    NotEnoughStockError,
)

from inventory.models import (
    Unit,
    Product,
    Order,
    Stock,
)

from .models import (
    Service,
    Transaction,
    Profit,
    ServiceCategory,
)
from .forms import (
    ServiceCreateForm,
    CategoryCreateForm,
    TransactionCreateForm,
)
from django.utils.translation import gettext_lazy as _


# -------------------- Category ----------------------------

@login_required
def create_category(request):
    form = CategoryCreateForm()
    if request.method == 'POST':
        form = CategoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list-category')
    context = {
        'form': form
    }
    return render(request, 'inventory/category_create.html', context)


@login_required
def update_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ServiceCategory, id=id)

    if request.method == 'GET':
        # pass the object as instance in form
        form = CategoryCreateForm(instance=obj)

    if request.method == 'POST':
        obj.icon.storage.delete(obj.icon.path)
        # pass the object as instance in form
        form = CategoryCreateForm(request.POST, request.FILES, instance=obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-category')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'inventory/category_create.html', context)


@login_required
def list_category(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ServiceCategory, id=id)
    obj.delete()
    return redirect('list-category')


@login_required
def update_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ServiceCategory, id=id)

    # pass the object as instance in form
    form = CategoryCreateForm(request.POST or None,
                              request.FILES or None, instance=obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        if os.path.exists(obj.icon.path):
            os.remove(obj.icon.path)
        form.save()
        return redirect('list-category')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'inventory/category_create.html', context)


# -------------------- Transaction ----------------------------


def renderCreateTransaction(request, form, product, order_id):
    context = {
        'form': form,
        'product': product,
        'order_id': order_id,
        'title': _("Create Transaction")
    }
    return render(request, 'inventory/transaction_create.html', context)


@login_required
def create_transaction(request, order_id, product_id):
    order = Order.objects.get(id=order_id)
    product = Service.objects.get(id=product_id)
    form = TransactionCreateForm(initial={'unit': product.unit})
    if request.method == 'POST':
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.product = product
            trans.save()
            return redirect('detail-order', id=order_id)
    return renderCreateTransaction(request, form, product, order_id)


@login_required
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(request.POST or None,
                                 instance=transaction)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-order', id=transaction.order.id)

    # add form dictionary to context
    context = {
        'form': form,
        'product': transaction.product,
        'order_id': transaction.order.id,
        'title': _("Update Transaction")
    }

    return render(request, 'inventory/transaction_create.html', context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    return render(request, 'inventory/transaction_detail.html', {'transaction': transaction,
                                                                 'amount': getTransactionAmount(transaction)})


def handle_transaction(transaction: Transaction, order: Order):
    pass


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    transaction.delete()
    return redirect('detail-order', id=transaction.order.id)


# -------------------- Service ----------------------------

@login_required
def create_service(request):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-product')
    context = {
        'form': form
    }
    return render(request, 'inventory/product_create.html', context)


@login_required
def update_service(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Service, id=id)

    # pass the object as instance in form
    form = ServiceCreateForm(request.POST or None,
                             instance=obj, title=_("Update Service"))

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-product')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'inventory/product_create.html', context)


def product_list_metadata(type, products: List[Service]):
    category_names = []
    categories = []
    alerts = 0
    for product in products:
        if product.type == type:
            # Average cost
            product.average_cost = 0
            if product.quantity > 0:
                product.average_cost = product.stock_price/product.quantity
            product.sell_price = product.average_cost * \
                (1 + product.suggested_price/100)
            # Categories
            if product.category.name not in category_names:
                category_names.append(product.category.name)
                categories.append(product.category)
            # Alerts
            if product.quantity < product.quantity_min:
                alerts += 1
    return (categories, alerts)


def prepare_service_list():
    products = Service.objects.all()
    (consumable_categories, consumable_alerts) = product_list_metadata(
        'consumable', products)
    (part_categories, part_alerts) = product_list_metadata('part', products)

    return {'products': products,
            'consumable_alerts': consumable_alerts,
            'consumable_categories': consumable_categories,
            'part_alerts': part_alerts,
            'part_categories': part_categories}


@login_required
def list_service(request):
    response = prepare_service_list()
    return render(request, 'inventory/product_list.html', response)


@login_required
def select_service(request, next, order_id):
    response = prepare_service_list()
    response.setdefault("next", next)
    response.setdefault("order_id", order_id)
    return render(request, 'inventory/product_select.html', response)


@login_required
def select_new_service(request, next, order_id):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect(next, order_id=order_id, product_id=product.id)
    context = {
        'form': form,
        'next': next,
        'order_id': order_id,
    }
    return render(request, 'inventory/product_create.html', context)


@login_required
def detail_service(request, id):
    # fetch the object related to passed id
    product = get_object_or_404(Service, id=id)
    product.average_cost = 0
    if product.quantity > 0:
        product.average_cost = product.stock_price/product.quantity
    product.sell_price = product.average_cost * \
        (1 + product.suggested_price/100)
    product.sell_max = product.average_cost * \
        (1 + product.max_price/100)

    stocks = Stock.objects.filter(product=product).order_by('-created_date')
    purchases = Transaction.objects.filter(
        product=product, order__type='purchase').order_by('-order__created_date')
    latest_purchase = purchases.first()
    latest_order = None
    if latest_purchase:
        latest_order = latest_purchase.order
    return render(request, 'inventory/product_detail.html', {'product': product,
                                                             'stocks': stocks,
                                                             'purchases': purchases,
                                                             'latest_order': latest_order})


@login_required
def delete_service(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Service, id=id)
    obj.delete()
    return redirect('list-product')
