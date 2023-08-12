from django.utils import timezone
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from users.models import (
    Associated,
)
from utils.models import (
    Order,
)

from inventory.models import (
    Product,
    ProductTransaction,
    Stock,
    convertUnit,
)
from inventory.forms import (
    OrderCreateForm,
)
from django.utils.translation import gettext_lazy as _

from .transaction import (
    handle_transaction,
    getTransactionAmount,
)


# -------------------- Order ----------------------------


@login_required
def create_order(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        last_purchase = ProductTransaction.objects.filter(order__type='purchase',
                                                          product=product).order_by('-id').first()
        if last_purchase:
            last_provider = last_purchase.order.associated
            # Search for a pending order from the same provider
            pending_order = Order.objects.filter(associated=last_provider,
                                                 status='pending').first()
            if pending_order:
                return redirect('create-transaction', pending_order.id, product_id)

        # Create new order from the
        return redirect('create-transaction-new-order', product_id)
    else:
        associated_id = request.session.get('associated_id')
        initial = {}
        if associated_id is not None:
            initial = {'associated': associated_id}
        form = OrderCreateForm(initial=initial)
        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.type = 'purchase'
                order.created_by = request.user
                order.save()
                return redirect('detail-order', id=order.id)
        context = {
            'form': form,
            'title': _("Create order"),
            'provider_list': Associated.objects.filter(type="provider", active=True)
        }
        return render(request, 'inventory/order_create.html', context)


@login_required
def select_provider(request):
    if request.method == 'POST':
        next = request.GET.get('next', 'create-order')
        provider = get_object_or_404(Associated, id=request.POST.get('id'))
        request.session['associated_id'] = provider.id
        return redirect(next)
    associates = Associated.objects.filter(
        type='provider', active=True).order_by("-created_date")
    return render(request, 'inventory/provider_list.html', {'associates': associates})


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)
    associated_id = request.session.get('associated_id')
    if associated_id is not None:
        associated = get_object_or_404(Associated, id=associated_id)
        order.associated = associated
        request.session['associated_id'] = None
    # pass the object as instance in form
    form = OrderCreateForm(instance=order)

    if request.method == 'POST':
        # pass the object as instance in form
        form = OrderCreateForm(request.POST, instance=order)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect('detail-order', id)

    # add form dictionary to context
    context = {
        'form': form,
        'title': _("Update order"),
        'provider_list': Associated.objects.filter(type="provider", active=True)
    }

    return render(request, 'inventory/order_create.html', context)


def undo_transaction(transaction: ProductTransaction):
    #  To be performed on complete orders
    product = Product.objects.get(id=transaction.product.id)

    # To be used in the rest of the system
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity)

    stock = Stock.objects.filter(product=product,
                                 quantity=product_quantity).latest('id')

    if stock is not None:
        cost = transaction.price*(1 + transaction.tax/100.)  # Add on taxes
        product.quantity -= product_quantity
        product.stock_price -= transaction.quantity * cost
        product.save()
        stock.delete()


@login_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)
    if status == 'complete':
        transactions = ProductTransaction.objects.filter(order=order)
        for transaction in transactions:
            handle_transaction(transaction)
        order.terminated_date = timezone.localtime(timezone.now())
    elif order.status == 'complete':
        if status == 'decline':
            # Reverse stock
            transactions = ProductTransaction.objects.filter(order=order)
            for transaction in transactions:
                undo_transaction(transaction)

    order.status = status
    order.save()
    return redirect('list-order')


STATUS_ORDER = ['pending', 'processing', 'approved', 'complete', 'decline']


@login_required
def list_order(request):
    context = prepareListOrder(request, ('processing', 'pending'))
    context.setdefault('stage', 'Terminated')
    context.setdefault('alternative_view', 'list-order-terminated')
    return render(request, 'inventory/order_list.html', context)


@login_required
def list_terminated_order(request):
    context = prepareListOrder(request, ('complete', 'decline'))
    context.setdefault('stage', 'Active')
    context.setdefault('alternative_view', 'list-order')
    return render(request, 'inventory/order_list.html', context)


def prepareListOrder(request, status_list):
    orders = Order.objects.filter(
        type='purchase', status__in=status_list).order_by('-created_date')
    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        transactions = ProductTransaction.objects.filter(order=order)
        amount = 0
        for transaction in transactions:
            amount += getTransactionAmount(transaction)
        order.amount = amount

    return {'orders': orders,
            'statuses': statuses}


@login_required
def detail_order(request, id):
    order = Order.objects.get(id=id)
    transactions = ProductTransaction.objects.filter(order=order)
    # Compute amount
    amount = 0
    for transaction in transactions:
        transaction.amount = transaction.quantity * \
            transaction.price*(1 + transaction.tax/100.)
        amount += transaction.amount
    order.amount = amount
    # Order by amount
    transactions = list(transactions)
    transactions.sort(key=lambda trans: trans.amount, reverse=True)
    # Terminated order
    terminated = order.status in ('decline', 'complete')
    empty = len(transactions) == 0
    return render(request, 'inventory/order_detail.html', {'order': order,
                                                           'transactions': transactions,
                                                           'terminated': terminated,
                                                           'empty': empty})
