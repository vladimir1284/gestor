import os
import pygsheets
import datetime
import json
from django.http import JsonResponse
from urllib.parse import urlsplit
from django.conf import settings
from django.utils import timezone
from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from services.models import Service

from inventory.models import (
    Product,
    ProductTransaction,
    Stock,
    convertUnit,
    PriceReference,
)
from inventory.forms import (
    ProductCreateForm,
    PriceReferenceCreateForm,
)
from django.utils.translation import gettext_lazy as _

from django.db.models import Avg, Sum
from statistics import mean, StatisticsError


class NotEnoughStockError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass

# -------------------- Product ----------------------------


def compute_product_stats(product: Product):
    # Monthly sells
    monthly_sels = []
    time_labels = []
    current_month = datetime.datetime.now().month
    for i in range(current_month, current_month - 12, -1):
        if i <= 0:
            i += 12
        time_labels.append(datetime.date(1900, i, 1).strftime('%b'))
        monthly_sels.append(int(
            ProductTransaction.objects.filter(
                order__type="sell",
                order__status="complete",
                order__terminated_date__month=i,
                product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0))

    max_monthly_sel = max(monthly_sels)
    yearly_sel = sum(monthly_sels)

    avg_cost, avg_price, avg_profit = average(product)

    return time_labels, yearly_sel, monthly_sels, max_monthly_sel, avg_cost, avg_price, avg_profit


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
        avg_cost, avg_price, avg_profit = average(product)
        product.average_cost = avg_cost
        product.average_price = avg_price

    return render(request, 'inventory/minprice_list.html', context)


def average(product: Product):
    transactions = ProductTransaction.objects.filter(
        order__type="sell",
        order__status="complete",
        product=product)

    try:
        avg_cost = mean([trans.cost/trans.quantity for trans in transactions])
    except StatisticsError as err:
        avg_cost = None
        if product.quantity != 0:
            avg_cost = product.stock_price/product.quantity
    except ZeroDivisionError as err:
        avg_cost = None

    try:
        avg_price = mean([trans.price for trans in transactions])
    except StatisticsError as err:
        avg_price = None
    except ZeroDivisionError as err:
        avg_price = None

    try:
        avg_profit = avg_price - avg_cost
    except:
        avg_profit = None
    return avg_cost, avg_price, avg_profit


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

    # Product statistics
    (time_labels, yearly_sel, monthly_sels, max_monthly_sel, avg_cost,
     avg_price, avg_profit) = compute_product_stats(product)

    return render(request, 'inventory/product_detail.html', {'product': product,
                                                             'stocks': stocks,
                                                             'purchases': purchases,
                                                             'latest_order': latest_order,
                                                             'price_references': price_references,
                                                             'time_labels': reversed(time_labels),
                                                             "yearly_sel": yearly_sel,
                                                             "monthly_sels": reversed(monthly_sels),
                                                             "max_monthly_sel": max_monthly_sel,
                                                             "avg_cost": avg_cost,
                                                             "avg_price": avg_price,
                                                             "avg_profit": avg_profit})


@ login_required
def delete_product(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id=id)
    obj.delete()
    return redirect('list-product')

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
