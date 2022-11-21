import os
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

from .models import (
    Product,
    Unit,
    Order,
    Transaction,
    Stock,
    Profit,
    StoreLocations,
    ProductCategory,
)
from .forms import (
    UnitCreateForm,
    ProductCreateForm,
    CategoryCreateForm,
    OrderCreateForm,
    TransactionCreateForm,
    TransactionProviderCreateForm,
)
from django.utils.translation import gettext_lazy as _


class DifferentMagnitudeUnitsError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass


class NotEnoughStockError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass


def convertUnit(input_unit, output_unit, value):
    iu = Unit.objects.get(name=input_unit)
    ou = Unit.objects.get(name=output_unit)
    if (iu.magnitude != ou.magnitude):
        raise DifferentMagnitudeUnitsError
    return value*iu.factor/ou.factor


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
    return render(request, 'store/addCategory.html', context)


@login_required
def update_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductCategory, id=id)

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

    return render(request, 'store/addCategory.html', context)


@login_required
def list_category(request):
    categories = ProductCategory.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductCategory, id=id)
    obj.delete()
    return redirect('list-category')


@login_required
def update_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductCategory, id=id)

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

    return render(request, 'store/addCategory.html', context)


# -------------------- Order ----------------------------

@login_required
def create_order(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        last_purchase = Transaction.objects.filter(order__type='purchase',
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
        form = OrderCreateForm()
        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                order = form.save()
                return redirect('detail-order', id=order.id)
        context = {
            'form': form
        }
        return render(request, 'store/addOrder.html', context)


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Order, id=id)

    # pass the object as instance in form
    form = OrderCreateForm(request.POST or None, instance=obj)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        order = form.save()
        return redirect('detail-order', id=order.id)

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'store/addOrder.html', context)


@login_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)
    order.status = status
    order.save()
    if status == 'complete':
        transactions = Transaction.objects.filter(order=order)
        for transaction in transactions:
            handle_transaction(transaction, order)
        return redirect('list-order')
    else:
        return redirect('detail-order', id=order.id)


@login_required
def list_order(request):
    orders = Order.objects.filter(
        type='purchase').order_by('-created_date')
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        transactions = Transaction.objects.filter(order=order)
        amount = 0
        for transaction in transactions:
            amount += getTransactionAmount(transaction)
        order.amount = amount
    return render(request, 'store/order_list.html', {'orders': orders,
                                                     'statuses': statuses})


@login_required
def detail_order(request, id):
    order = Order.objects.get(id=id)
    transactions = Transaction.objects.filter(order=order)
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
    terminated = order.status in ['decline', 'complete']
    return render(request, 'store/order_detail.html', {'order': order,
                                                       'transactions': transactions,
                                                       'terminated': terminated})


# -------------------- Transaction ----------------------------

def getNewOrder(associated: Associated, product: Product):
    return Order.objects.create(concept="Restock of {}".format(product.name),
                                note="Automatically created for the purchase of product {}. Please, check all details!".format(
        product.name),
        type='purchase',
        associated=associated)


def renderCreateTransaction(request, form, product, order_id):
    context = {
        'form': form,
        'product': product,
        'order_id': order_id,
        'title': _("Create Transaction")
    }
    return render(request, 'store/addTransaction.html', context)


@login_required
def create_transaction(request, order_id, product_id):
    order = Order.objects.get(id=order_id)
    product = Product.objects.get(id=product_id)
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
def create_transaction_new_order(request, product_id):
    product = Product.objects.get(id=product_id)
    initial = {'unit': product.unit}
    last_purchase = Transaction.objects.filter(order__type='purchase',
                                               product=product).order_by('-id').first()
    order_id = -1
    if last_purchase:
        form = TransactionCreateForm(initial=initial)
    else:
        form = TransactionProviderCreateForm(initial=initial)
    if request.method == 'POST':
        if last_purchase:
            form = TransactionCreateForm(request.POST)
        else:
            form = TransactionProviderCreateForm(request.POST)
        if form.is_valid():
            if last_purchase:
                last_provider = last_purchase.order.associated
            else:
                last_provider = form.cleaned_data['associated']

            order = getNewOrder(last_provider, product)
            trans = form.save(commit=False)
            trans.order = order
            trans.product = product
            trans.save()
            return redirect('detail-order', id=order.id)
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

    return render(request, 'store/addTransaction.html', context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    return render(request, 'store/transaction_detail.html', {'transaction': transaction,
                                                             'amount': getTransactionAmount(transaction)})


def getTransactionAmount(transaction: Transaction):
    return transaction.quantity * \
        transaction.price*(1 + transaction.tax/100.)


def handle_transaction(transaction: Transaction, order: Order):
    #  To be performed on complete orders
    product = transaction.product
    # To be used in the rest of the system
    product = Product.objects.get(id=product.id)
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity)

    # TODO study taxes handling on sales to improve these formula
    if (order.type == 'sell'):
        # Generate profit
        income = transaction.price * \
            (1 - transaction.tax/100.)*transaction.quantity  # Take off taxes
        if (product_quantity > product.quantity):
            raise NotEnoughStockError

        # Implementing FIFO method
        stock_cost = 0
        pending = product_quantity
        stock_array = Stock.objects.filter(
            product=product).order_by('created_date')
        for stock in stock_array:
            if (pending < stock.quantity):
                stock_cost += pending * stock.cost
                stock.quantity -= pending
                stock.save()
                break
            elif (pending == stock.quantity):
                stock_cost += stock.quantity * stock.cost
                stock.delete()
                break
            else:
                stock_cost += stock.quantity * stock.cost
                pending -= stock.quantity
                stock.delete()

        profit = income - stock_cost
        Profit.objects.create(product=product,
                              quantity=product_quantity,
                              profit=profit)
        product.quantity -= product_quantity
        product.stock_price -= stock_cost
        product.save()
    elif (order.type == 'purchase'):
        # Generate stock
        cost = transaction.price*(1 + transaction.tax/100.)  # Add on taxes
        Stock.objects.create(product=product,
                             quantity=product_quantity,
                             cost=cost)
        product.quantity += product_quantity
        product.stock_price += product_quantity * cost
        product.save()


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(Transaction, id=id)
    transaction.delete()
    return redirect('detail-order', id=transaction.order.id)


# -------------------- Unit ----------------------------

# TODO delete units

@login_required
def create_unit(request):
    form = UnitCreateForm()
    if request.method == 'POST':
        form = UnitCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-unit')
    context = {
        'form': form
    }
    return render(request, 'store/addUnit.html', context)


@login_required
def list_unit(request):
    units = Unit.objects.all()
    return render(request, 'store/unit_list.html', {'units': units})


# -------------------- Product ----------------------------

@login_required
def create_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-product')
    context = {
        'form': form
    }
    return render(request, 'store/addProduct.html', context)


@login_required
def update_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)

    # pass the object as instance in form
    form = ProductCreateForm(request.POST or None,
                             instance=obj, title=_("Update Product"))

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-product')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'store/addProduct.html', context)


def prepare_product_list():
    products = Product.objects.all()
    consumable_alerts = 0
    part_alerts = 0
    category_names = []
    categories = []
    for product in products:
        product.average_cost = 0
        if product.category.name not in category_names:
            category_names.append(product.category.name)
            categories.append(product.category)
        if product.quantity > 0:
            product.average_cost = product.stock_price/product.quantity
        product.sell_price = product.average_cost * \
            (1 + product.suggested_price/100)
        if product.quantity < product.quantity_min:
            if product.type == 'part':
                part_alerts += 1
            if product.type == 'consumable':
                consumable_alerts += 1

    return {'products': products,
            'consumable_alerts': consumable_alerts,
            'part_alerts': part_alerts,
            'categories': categories}


@login_required
def list_product(request):
    response = prepare_product_list()
    return render(request, 'store/product_list.html', response)


@login_required
def select_product(request, next, order_id):
    response = prepare_product_list()
    response.setdefault("next", next)
    response.setdefault("order_id", order_id)
    return render(request, 'store/product_select.html', response)


@login_required
def select_new_product(request, next, order_id):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect(next, order_id=order_id, product_id=product.id)
    context = {
        'form': form,
        'next': next,
        'order_id': order_id,
    }
    return render(request, 'store/addProduct.html', context)


@login_required
def detail_product(request, id):
    # fetch the object related to passed id
    product = get_object_or_404(Product, id=id)
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
    return render(request, 'store/product_detail.html', {'product': product,
                                                         'stocks': stocks,
                                                         'purchases': purchases,
                                                         'latest_order': latest_order})


@login_required
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)
    obj.delete()
    return redirect('list-product')
