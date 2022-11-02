from django.shortcuts import render, redirect
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
        form = CategoryCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            ProductCategory.objects.create(name=name)
            return redirect('/store/list-category')
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
            concept = form.cleaned_data['concept']
            type = form.cleaned_data['type']
            note = form.cleaned_data['note']
            associated = form.cleaned_data['associated']
            order = Order.objects.create(concept=concept,
                                         type=type,
                                         associated=associated,
                                         note=note)
            formset = TransactionFormset(request.POST)
            for form in formset:
                if form.is_valid():
                    handle_transaction(form, order)
            return redirect('/store/list-order')
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'store/addOrder.html', context)


def handle_transaction(form: ModelForm, order: Order):
    note = form.cleaned_data.get('note')
    product: Product = form.cleaned_data.get('product')
    tax = form.cleaned_data.get('tax')
    price = form.cleaned_data.get('price')
    unit = form.cleaned_data.get('unit')
    order_quantity = form.cleaned_data.get('quantity')
    Transaction.objects.create(order=order,
                               product=product,
                               unit=unit,
                               tax=tax,
                               price=price,
                               note=note,
                               quantity=order_quantity)
    # To be used in the rest of the system
    product = Product.objects.get(id=product.id)
    product_quantity = convertUnit(
        input_unit=unit, output_unit=product.unit, value=order_quantity)

    # TODO study taxes handling on sales to improve these formula
    if (order.type == 'sell'):
        # Generate profit
        income = price*(1 - tax/100.)*order_quantity  # Take off taxes
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
        cost = price*(1 + tax/100.)  # Add on taxes
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
            name = form.cleaned_data['name']
            factor = form.cleaned_data['factor']
            magnitude = form.cleaned_data['magnitude']
            Unit.objects.create(name=name,
                                factor=factor,
                                magnitude=magnitude)
            return redirect('/store/list-unit')
    context = {
        'form': form
    }
    return render(request, 'store/addUnit.html', context)


@login_required
def create_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            unit = form.cleaned_data['unit']
            category = form.cleaned_data['category']
            type = form.cleaned_data['type']
            sell_price = form.cleaned_data['sell_price']
            sell_tax = form.cleaned_data['sell_tax']
            sell_price_min = form.cleaned_data['sell_price_min']
            sell_price_max = form.cleaned_data['sell_price_max']
            quantity_min = form.cleaned_data['quantity_min']
            image = form.cleaned_data['image']
            Product.objects.create(name=name,
                                   description=description,
                                   unit=unit,
                                   category=category,
                                   type=type,
                                   sell_price=sell_price,
                                   sell_tax=sell_tax,
                                   sell_price_min=sell_price_min,
                                   sell_price_max=sell_price_max,
                                   quantity_min=quantity_min,
                                   image=image
                                   )
            return redirect('/store/list-product')
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
            name = form.cleaned_data['name']
            company = form.cleaned_data['company']
            address = form.cleaned_data['address']
            note = form.cleaned_data['note']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            type = form.cleaned_data['type']
            avatar = form.cleaned_data['avatar']
            Associated.objects.create(name=name,
                                      company=company,
                                      address=address,
                                      note=note,
                                      email=email,
                                      phone_number=phone_number,
                                      type=type,
                                      avatar=avatar
                                      )
            return redirect('/store/list-associated')
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
def list_product(request):
    products = Product.objects.all()
    consumable_alerts = 0
    part_alerts = 0
    for product in products:
        product.average_cost = 0
        if product.quantity > 0:
            product.average_cost = product.stock_price/product.quantity
        if product.quantity < product.quantity_min:
            if product.type == 'part':
                part_alerts += 1
            if product.type == 'consumable':
                consumable_alerts += 1

    return render(request, 'store/product_list.html', {'products': products,
                                                       'consumable_alerts': consumable_alerts,
                                                       'part_alerts': part_alerts})
