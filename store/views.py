import os
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    HttpResponseRedirect)
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

from users.models import User
from .models import (
    Associated,
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
    AssociatedCreateForm,
    OrderCreateForm,
    TransactionFormset
)
CAT_COLORS = ['secondary', 'success', 'danger',
              'warning', 'info', 'dark', 'primary']


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
def delete_category(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductCategory, id=id)
    obj.delete()
    return redirect('/store/list-category')


@login_required
def update_category(request, id):
    # dictionary for initial data with
    # field names as keys
    context = {}

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
        return redirect('/store/list-category')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'store/addCategory.html', context)


@login_required
def create_order(request):
    form = OrderCreateForm()
    formset = TransactionFormset()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            formset = TransactionFormset(request.POST)
            for form in formset:
                if form.is_valid():
                    transaction = form.save(commit=False)
                    transaction.order = order
                    transaction.save()
                    handle_transaction(transaction, order)
            return redirect('list-order')
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'store/addOrder.html', context)


def handle_transaction(transaction: Transaction, order: Order):
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
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)
    obj.delete()
    return redirect('list-product')


@login_required
def update_product(request, id):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)

    # pass the object as instance in form
    form = CategoryCreateForm(request.POST or None,
                              request.FILES or None, instance=obj)

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


@login_required
def create_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list-product')
    context = {
        'form': form
    }
    return render(request, 'store/addProduct.html', context)


@login_required
def create_associated(request):
    form = AssociatedCreateForm()
    if request.method == 'POST':
        form = AssociatedCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list-associated')
    context = {
        'form': form
    }
    return render(request, 'store/addAssociated.html', context)


@login_required
def list_unit(request):
    units = Unit.objects.all()
    return render(request, 'store/unit_list.html', {'units': units})


@login_required
def list_category(request):
    categories = ProductCategory.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


@login_required
def list_associated(request):
    associates = Associated.objects.all()
    return render(request, 'store/associated_list.html', {'associates': associates})


@login_required
def list_order(request):
    orders = Associated.objects.all()
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def list_product(request):
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

    return render(request, 'store/product_list.html', {'products': products,
                                                       'consumable_alerts': consumable_alerts,
                                                       'part_alerts': part_alerts,
                                                       'categories': categories})
