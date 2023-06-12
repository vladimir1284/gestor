import os
from django.core.checks.messages import Error
import pygsheets
import json
from django.http import JsonResponse
from urllib.parse import urlsplit
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from typing import List
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from services.models import Service

from users.models import (
    Associated,
)
from utils.models import (
    Order,
)

from services.models import ServiceTransaction

from .models import (
    Product,
    Unit,
    ProductTransaction,
    Stock,
    ProductCategory,
    convertUnit,
    PriceReference,
    ProductKit,
    KitElement,
    KitService
)
from .forms import (
    UnitCreateForm,
    ProductCreateForm,
    PriceReferenceCreateForm,
    CategoryCreateForm,
    TransactionCreateForm,
    TransactionProviderCreateForm,
    OrderCreateForm,
    KitCreateForm,
    KitElementCreateForm,
    KitTransactionCreateForm,
)
from django.utils.translation import gettext_lazy as _


class NotEnoughStockError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass


# -------------------- Category ----------------------------

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'utils/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(ProductCategory, id=id)
    category.delete()
    return redirect('list-category')


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
        order.terminated_date = timezone.now()
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


# -------------------- Transaction ----------------------------

def getNewOrder(associated: Associated, product: Product, user):
    return Order.objects.create(concept="Restock of {}".format(product.name),
                                note="Automatically created for the purchase of product {}. Please, check all details!".format(
        product.name),
        type='purchase',
        associated=associated,
        created_by=user)


def renderCreateTransaction(request, form, product: Product, order_id):
    price_references = PriceReference.objects.filter(product=product)
    units = [product.unit]
    units_qs = Unit.objects.filter(
        magnitude=product.unit.magnitude).exclude(id=product.unit.id)
    for unit in units_qs:
        units.append(unit)
    title = _("Create Transaction")
    if product.type == "part":
        title = _("Add part")
    if product.type == "consumable":
        title = _("Add consumable")
    context = {
        'form': form,
        'product': product,
        'suggested': product.getSuggestedPrice(),
        'cost': product.getCost(),
        'order_id': order_id,
        'price_references': price_references,
        'title': title,
        'units': units,
        'create': True,
    }
    return context


@login_required
def create_transaction(request, order_id, product_id):
    order = Order.objects.get(id=order_id)
    product = Product.objects.get(id=product_id)

    form = TransactionCreateForm(initial={'unit': product.unit,
                                          'price': product.getSuggestedPrice()},
                                 product=product, order=order)
    if request.method == 'POST':
        form = TransactionCreateForm(
            request.POST, product=product, order=order)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.product = product
            trans.save()
            if order.type == 'sell':
                return redirect('detail-service-order', id=order_id)
            if order.type == 'purchase':
                return redirect('detail-order', id=order_id)
    context = renderCreateTransaction(request, form, product, order_id)
    return render(request, 'inventory/transaction_create.html', context)


@login_required
def create_kit_transaction(request, order_id, kit_id):
    order = get_object_or_404(Order, id=order_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    (elements, services, total, min_price) = computeKitData(kit)

    form = KitTransactionCreateForm(initial={
        'quantity': 1,
        'price': total,
        'tax': False
    }, min_price=min_price)

    if request.method == 'POST':
        form = KitTransactionCreateForm(request.POST, initial={
            'quantity': 1,
            'price': total,
            'tax': False
        }, min_price=min_price, kit=kit)

        if form.is_valid():
            multiply = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            tax = form.cleaned_data['tax']
            print(tax)

            # Handle price change
            load2service = 0
            if price != total:
                diff = price - total
                if diff < 0:  # Discount
                    order.discount = -multiply*diff
                    order.save()
                else:  # Profit
                    load2service = multiply*diff

            # Add services
            kitServices = KitService.objects.filter(kit=kit)
            transactions = ServiceTransaction.objects.filter(order=order)
            for service in kitServices:
                inOrder = False
                # Check for products in the order
                for trans in transactions:
                    if service.service == trans.service:
                        # Add to a product present in the order
                        trans.quantity += multiply
                        trans.price += load2service/trans.quantity
                        trans.save()
                        inOrder = True
                        break
                if not inOrder:
                    # New product transaction
                    if load2service > 0:
                        service.service.suggested_price += load2service/multiply
                    trans = ServiceTransaction.objects.create(
                        order=order,
                        service=service.service,
                        quantity=multiply,
                        note=_(
                            F"Generated from kit {kit.name}.\nRemember to check the price and tax!"),
                        price=service.service.suggested_price
                    )
                    if tax == False:
                        trans.tax = 0
                        trans.save()
                load2service = 0

            # Add products
            elements = KitElement.objects.filter(kit=kit)
            transactions = ProductTransaction.objects.filter(order=order)
            for element in elements:
                inOrder = False
                # Check for products in the order
                for trans in transactions:
                    if element.product == trans.product:
                        # Add to a product present in the order
                        trans.quantity += multiply*convertUnit(element.unit,
                                                               trans.unit,
                                                               element.quantity)
                        trans.save()
                        inOrder = True
                        break
                if not inOrder:
                    # New product transaction
                    trans = ProductTransaction.objects.create(
                        order=order,
                        product=element.product,
                        quantity=element.quantity*multiply,
                        unit=element.unit,
                        note=_(
                            F"Generated from kit {kit.name}.\nRemember to check the price and tax!"),
                        price=element.product.getSuggestedPrice()
                    )
                    if tax == False:
                        trans.tax = 0
                        trans.save()

            return redirect('detail-service-order', id=order_id)

    context = {
        'kit': kit,
        'elements': elements,
        'services': services,
        'total': total,
        'form': form
    }
    return render(request, 'inventory/kit_add.html', context)


@login_required
def create_transaction_new_order(request, product_id):
    product = Product.objects.get(id=product_id)
    initial = {'unit': product.unit}
    last_purchase = ProductTransaction.objects.filter(order__type='purchase',
                                                      product=product).order_by('-id').first()
    order_id = -1
    if last_purchase:
        form = TransactionCreateForm(
            initial=initial, product=product)
    else:
        form = TransactionProviderCreateForm(
            initial=initial, product=product)
    if request.method == 'POST':
        if last_purchase:
            last_provider = last_purchase.order.associated
        else:
            last_provider = Associated.objects.get(
                id=int(request.POST['associated']))
        order = getNewOrder(last_provider, product, request.user)
        if last_purchase:
            form = TransactionCreateForm(
                request.POST, product=product, order=order)
        else:
            form = TransactionProviderCreateForm(
                request.POST, product=product, order=order)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.product = product
            trans.save()
            return redirect('detail-order', id=order.id)
    context = renderCreateTransaction(request, form, product, order_id)
    return render(request, 'inventory/transaction_create.html', context)


@login_required
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ProductTransaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(request.POST or None,
                                 instance=transaction,
                                 id=transaction.id,
                                 product=transaction.product,
                                 order=transaction.order)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        if transaction.order.type == 'sell':
            return redirect('detail-service-order', id=transaction.order.id)
        if transaction.order.type == 'purchase':
            return redirect('detail-order', id=transaction.order.id)

    # add form dictionary to context
    context = renderCreateTransaction(request, form, transaction.product,
                                      transaction.order.id)
    context['title'] = _("Update Transaction")
    context['create'] = False
    return render(request, 'inventory/transaction_create.html', context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ProductTransaction, id=id)
    return render(request, 'inventory/transaction_detail.html', {'transaction': transaction,
                                                                 'amount': getTransactionAmount(transaction)})


def getTransactionAmount(transaction: ProductTransaction):
    return transaction.quantity * \
        transaction.price*(1 + transaction.tax/100.)


def handle_transaction(transaction: ProductTransaction):
    #  To be performed on complete orders
    product = Product.objects.get(id=transaction.product.id)

    # To be used in the rest of the system
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity)

    # TODO study taxes handling on sales to improve these formula
    # Generate stock
    cost = transaction.price*(1 + transaction.tax/100.)  # Add on taxes
    product.quantity += product_quantity
    product.stock_price += transaction.quantity * cost
    product.save()
    Stock.objects.create(product=product,
                         quantity=product_quantity,
                         cost=(transaction.quantity * cost)/product_quantity)


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ProductTransaction, id=id)
    transaction.delete()
    if transaction.order.type == 'sell':
        return redirect('detail-service-order', id=transaction.order_id)
    if transaction.order.type == 'purchase':
        return redirect('detail-order', id=transaction.order_id)


# -------------------- Unit ----------------------------


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
    return render(request, 'inventory/unit_create.html', context)


@login_required
def update_unit(request, id):
    # fetch the object related to passed id
    unit = get_object_or_404(Unit, id=id)
    if not Product.objects.filter(unit=unit):
        unit.can_delete = True

    # pass the object as instance in form
    form = UnitCreateForm(request.POST or None,
                          instance=unit)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('list-unit')

    # add form dictionary to context
    context = {
        'form': form,
    }

    return render(request, 'inventory/unit_update.html', context)


@login_required
def list_unit(request):
    units = Unit.objects.all()
    return render(request, 'inventory/unit_list.html', {'units': units})


@login_required
def delete_unit(request, id):
    # fetch the object related to passed id
    unit = get_object_or_404(Unit, id=id)
    unit.delete()
    return redirect('list-unit')


# -------------------- Price Reference ----------------------------

@login_required
def create_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = PriceReferenceCreateForm()
    if request.method == 'POST':
        form = PriceReferenceCreateForm(request.POST)
        if form.is_valid():
            price = form.save(commit=False)
            price.product = product
            price.updated_date = timezone.now()
            price.save()
            return redirect('detail-product', product_id)
    context = {
        'form': form
    }
    return render(request, 'inventory/price_create.html', context)


@login_required
def update_price(request, id):
    # fetch the object related to passed id
    price = get_object_or_404(PriceReference, id=id)
    price.updated_date = timezone.now()

    # pass the object as instance in form
    form = PriceReferenceCreateForm(request.POST or None,
                                    instance=price)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-product', price.product.id)

    # add form dictionary to context
    context = {
        'form': form,
    }

    return render(request, 'inventory/price_create.html', context)


@login_required
def delete_price(request, id):
    # fetch the object related to passed id
    price = get_object_or_404(PriceReference, id=id)
    price.delete()
    return redirect('detail-product', price.product.id)

# -------------------- Product ----------------------------


def populate_product(type):
    # Header row
    header = ['Nombre', 'Categoría', 'Unidad', 'Precio', 'Cantidad']
    data = [header]
    parts = Product.objects.filter(type=type).order_by("category")
    for part in parts:
        data.append([
            part.name,
            part.category.name,
            part.unit.name,
            part.min_price,
            part.stock_price])
    return data


@login_required
def export_inventory(request):
    service_file = os.path.join(
        settings.BASE_DIR, 'trailer-rental-323614-d43be7453c41.json')
    gc = pygsheets.authorize(service_file=service_file)

    # open the google spreadsheet (where 'test' is the name of my sheet)
    sh = gc.open('Inventario')

    # ------------------------------ Parts -------------------------------------
    # select the first sheet
    wks = sh.worksheet('title', 'partes')
    # upload the data.
    wks.update_values(crange="A1", values=populate_product('part'))

    # --------------------------- Consumables ----------------------------------
    wks = sh.worksheet('title', 'insumos')
    wks.update_values(crange="A1", values=populate_product('consumable'))

    return redirect('https://docs.google.com/spreadsheets/d/1P5R4KUYcrxqCN3D-nDsDbBOJaPyDjARFlI_wPabdrT8/edit?usp=sharing')


@login_required
def create_product(request):
    form = ProductCreateForm()
    if request.method == 'POST':
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect('detail-product', product.id)
    context = {
        'form': form
    }
    return render(request, 'inventory/product_create.html', context)


@login_required
def update_product(request, id):
    # fetch the object related to passed id
    product = get_object_or_404(Product, id=id)

    # pass the object as instance in form
    form = ProductCreateForm(request.POST or None,
                             request.FILES or None,
                             instance=product)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-product', id)

    # add form dictionary to context
    context = {
        'form': form,
    }

    return render(request, 'inventory/product_create.html', context)


def product_list_metadata(type, products: List[Product]):
    category_names = []
    categories = []
    alerts = 0
    for product in products:
        if product.type == type:
            product.average_cost = product.getCost()
            # Average cost
            product.sell_price = product.getSuggestedPrice()
            # Categories
            if product.category and product.category.name not in category_names:
                category_names.append(product.category.name)
                categories.append(product.category)
            # Alerts
            if product.quantity < product.quantity_min:
                alerts += 1
    return (categories, alerts)


def computeTransactionProducts(product, status):
    quantity = 0
    transactions = ProductTransaction.objects.filter(
        product=product, order__status=status, order__type='purchase')
    for transaction in transactions:
        quantity += transaction.quantity
    return quantity


def prepare_product_list(products=None):
    if products is None:
        products = Product.objects.all().order_by('name')
    (consumable_categories, consumable_alerts) = product_list_metadata(
        'consumable', products)
    (part_categories, part_alerts) = product_list_metadata('part', products)
    for product in products:
        # Pending quantity
        pending = computeTransactionProducts(product, 'pending')
        if pending > 0:
            product.pending = pending
        # Processing quantity
        processing = computeTransactionProducts(product, 'processing')
        if processing > 0:
            product.processing = processing

    return {'products': products,
            'consumable_alerts': consumable_alerts,
            'consumable_categories': consumable_categories,
            'part_alerts': part_alerts,
            'part_categories': part_categories}


@login_required
def list_product(request):
    context = prepare_product_list()
    return render(request, 'inventory/product_list.html', context)


@login_required
def minprice_update(request):
    if request.method == "POST":
        try:
            post_data = json.loads(request.body.decode("utf-8"))
            product = Product.objects.get(id=post_data["product_id"])
            product.min_price = post_data["value"]
            product.save()
            return JsonResponse({"status": "ok",
                                "new_value": F"${product.min_price}"})
        except Exception as err:
            print(err)
            return JsonResponse({"status": "error",
                                 "msg": str(err)})
    return JsonResponse({})


def discountStockFIFO(product, product_quantity):
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
    return stock_cost


@login_required
def quantity_update(request):
    if request.method == "POST":
        try:
            post_data = json.loads(request.body.decode("utf-8"))
            product = Product.objects.get(id=post_data["product_id"])
            new_quantity = post_data["value"]

            if new_quantity < 0:
                return JsonResponse({"status": "error",
                                     "msg": "Negative quantity!!"})

            diff = new_quantity - product.quantity
            if diff > 0:
                # Emulate a purchase transaction by adding the quantity to the latest stock
                last_stock = Stock.objects.filter(product=product).latest('id')
                last_stock.quantity += diff
                last_stock.save()
                product.quantity = new_quantity
                product.stock_price += diff*last_stock.cost
                product.save()
            elif diff < 0:
                # Emulate a sell transaction
                stock_cost = discountStockFIFO(product, -diff)
                product.quantity += diff
                product.stock_price -= stock_cost
                product.save()

            return JsonResponse({"status": "ok",
                                "new_value": product.quantity})
        except Exception as err:
            print(err)
            return JsonResponse({"status": "error",
                                 "msg": str(err)})
    return JsonResponse({})


@login_required
def minprice_product(request):
    context = prepare_product_list()

    # TODO Exclude TOWIT services
    for product in context['products']:

        # Show references
        product.price_references = PriceReference.objects.filter(
            product=product)

        for ref in product.price_references:
            split_url = urlsplit(ref.url)
            ref.favicon = split_url.scheme + "://" + split_url.netloc + "/favicon.ico"

        # Compute average sell price
        transactions = ProductTransaction.objects.filter(
            order__type="sell",
            order__status="complete",
            product=product).order_by('-id')[:10]
        total = 0
        quantity = 0
        for transaction in transactions:
            product_quantity = convertUnit(
                input_unit=transaction.unit,
                output_unit=product.unit,
                value=transaction.quantity)
            quantity += product_quantity
            total += transaction.cost
        if quantity > 0:
            product.average = total/quantity

    return render(request, 'inventory/minprice_list.html', context)


def service_list_metadata(services: List[Service]):
    category_names = []
    categories = []
    for service in services:
        # Categories
        if service.category and service.category.name not in category_names:
            category_names.append(service.category.name)
            categories.append(service.category)
    return categories


@login_required
def select_product(request, next, order_id):
    context = prepare_product_list()

    context.setdefault("next", next)
    context.setdefault("order_id", order_id)
    return render(request, 'inventory/product_select.html', context)


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
    return render(request, 'inventory/product_create.html', context)


@login_required
def duplicate_product(request, id):
    print("here")
    product = get_object_or_404(Product, id=id)
    product.image = None
    product.pk = None
    product.name += " (copy)"
    product.stock_price = 0
    product.quantity = 0
    product._state.adding = True
    product.save()
    return redirect('detail-product', product.pk)


@ login_required
def detail_product(request, id):
    # fetch the object related to passed id
    product = get_object_or_404(Product, id=id)
    if not ProductTransaction.objects.filter(product=product):
        product.can_delete = True
    product.average_cost = product.getCost()
    product.sell_price = product.getSuggestedPrice()

    stocks = Stock.objects.filter(product=product).order_by('-created_date')
    purchases = ProductTransaction.objects.filter(
        product=product, order__type='purchase',
        order__status='complete').order_by('-order__created_date')
    latest_purchase = purchases.first()
    latest_order = None
    if latest_purchase:
        latest_order = latest_purchase.order
    # Pending quantity
    pending = computeTransactionProducts(product, 'pending')
    if pending > 0:
        product.pending = pending
    # Processing quantity
    processing = computeTransactionProducts(product, 'processing')
    if processing > 0:
        product.processing = processing
    # Price references
    price_references = PriceReference.objects.filter(product=product)
    return render(request, 'inventory/product_detail.html', {'product': product,
                                                             'stocks': stocks,
                                                             'purchases': purchases,
                                                             'latest_order': latest_order,
                                                             'price_references': price_references})


@ login_required
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)
    obj.delete()
    return redirect('list-product')


# --------------------------- Kits --------------------------------

@login_required
def create_kit(request):
    form = KitCreateForm()
    if request.method == 'POST':
        form = KitCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-kit')
    context = {
        'form': form,
        'title': _("Create Kit")
    }
    return render(request, 'inventory/kit_create.html', context)


@login_required
def update_kit(request, id):
    # fetch the object related to passed id
    kit = get_object_or_404(ProductKit, id=id)

    # pass the object as instance in form
    form = KitCreateForm(request.POST or None,
                         instance=kit)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-kit', id)
    context = {
        'form': form,
        'title': _("Update kit")
    }

    return render(request, 'inventory/kit_create.html', context)


def computeKitData(kit):
    elements = KitElement.objects.filter(kit=kit)
    total = 0
    min_price = 0
    for element in elements:
        # Add cost
        total += element.quantity*convertUnit(
            element.product.unit,
            element.unit,
            element.product.getSuggestedPrice())
        min_price += element.quantity*convertUnit(
            element.product.unit,
            element.unit,
            element.product.min_price)
        # Compute availability
        element.product.available = convertUnit(
            element.product.unit,
            element.unit,
            element.product.computeAvailable())

    services = KitService.objects.filter(kit=kit)
    for service in services:
        total += service.service.suggested_price

    return (elements, services, total, min_price)


@login_required
def list_kit(request):
    kits = ProductKit.objects.all()

    for kit in kits:
        (elements, services, total, min_price) = computeKitData(kit)
        kit.total = total

    context = {
        'kits': kits,
    }
    return render(request, 'inventory/kit_list.html', context)


@login_required
def detail_kit(request, id):
    # fetch the object related to passed id
    kit = get_object_or_404(ProductKit, id=id)

    (elements, services, total, min_price) = computeKitData(kit)

    context = {
        'kit': kit,
        'elements': elements,
        'services': services,
        'total': total,
    }
    return render(request, 'inventory/kit_detail.html', context)


@ login_required
def delete_kit(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(ProductKit, id=id)
    obj.delete()
    return redirect('list-kit')


# --------------------------- Kit Elements --------------------------------

@login_required
def select_kit_product(request, kit_id):
    context = prepare_product_list()

    # Adding services to kit
    services = Service.objects.all()
    context.setdefault('services', services)
    context.setdefault('categories', service_list_metadata(services))

    context.setdefault("kit_id", kit_id)
    return render(request, 'inventory/kit_product_select.html', context)


@login_required
def create_kit_element(request, kit_id, product_id):
    product = get_object_or_404(Product, id=product_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    form = KitElementCreateForm(initial={'unit': product.unit})
    if request.method == 'POST':
        form = KitElementCreateForm(request.POST)
        if form.is_valid():
            kitElement = form.save(commit=False)
            kitElement.kit = kit
            kitElement.product = product
            kitElement.save()
            return redirect('detail-kit', kit_id)
    context = {
        'form': form,
        'kit': kit,
        'product': product,
        'title': _("Add kit product")
    }
    return render(request, 'inventory/kit_element_create.html', context)


@login_required
def update_kit_element(request, id):
    # fetch the object related to passed id
    kitElement = get_object_or_404(KitElement, id=id)

    # pass the object as instance in form
    form = KitElementCreateForm(request.POST or None,
                                instance=kitElement)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-kit', kitElement.kit.id)
    context = {
        'form': form,
        'title': _("Update kit product")
    }

    return render(request, 'inventory/kit_element_create.html', context)


@ login_required
def delete_kit_element(request, id):
    # fetch the object related to passed id
    kitElement = get_object_or_404(KitElement, id=id)
    kitElement.delete()
    return redirect('detail-kit', kitElement.kit.id)


# --------------------------- Kit Services --------------------------------


@login_required
def create_kit_service(request, kit_id, service_id):
    service = get_object_or_404(Service, id=service_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    KitService.objects.create(kit=kit, service=service)
    return redirect('detail-kit', kit_id)


@ login_required
def delete_kit_service(request, id):
    # fetch the object related to passed id
    kitService = get_object_or_404(KitService, id=id)
    kitService.delete()
    return redirect('detail-kit', kitService.kit.id)
