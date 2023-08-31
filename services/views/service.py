from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from inventory.models import (
    ProductTransaction,
    Product,
    ProductKit,
    KitElement,
)
from utils.models import Order
from inventory.models import convertUnit
from inventory.views.product import (
    prepare_product_list,
)
from services.models import (
    Service,
    ServiceTransaction,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from services.forms import (
    ServiceCreateForm,
)
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F

# -------------------- Service ----------------------------


@login_required
def create_service(request):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-service')
    context = {
        'form': form
    }
    return render(request, 'services/service_create.html', context)


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
        return redirect('list-service')

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'services/service_create.html', context)


def service_list_metadata(services: List[Service]):
    category_names = []
    categories = []
    for service in services:
        # Categories
        if service.category and service.category.name not in category_names:
            category_names.append(service.category.name)
            categories.append(service.category)
    return categories


def prepare_service_list(order_id=None):
    services = Service.objects.annotate(
        total_quantity=Sum('servicetransaction__quantity')
    ).annotate(
        total_income=Sum(F('servicetransaction__quantity')
                         * F('servicetransaction__price'))
    ).order_by('-total_income')
    # Pareto computation
    total_income_sum = services.aggregate(total_income_sum=Sum('total_income'))
    accumulated = 0
    for service in services:
        if service.total_income:
            accumulated += service.total_income
            if accumulated/total_income_sum['total_income_sum'] < 0.8:
                service.pareto = True
    products = Product.objects.filter(active=True).order_by('name')
    products_in_order = []

    # Don't include products in the current order
    if order_id is not None:
        transactions = ProductTransaction.objects.filter(order__id=order_id)
        products_in_order = [trans.product for trans in transactions]

    product_list = []
    for product in products:
        if product not in products_in_order:
            product.available = product.computeAvailable()
            if product.available > 0:
                product_list.append(product)
            elif order_id is not None:
                order = get_object_or_404(Order, pk=order_id)
                if order.quotation:
                    product_list.append(product)

    context = prepare_product_list(product_list)
    context.setdefault('services', services)
    context.setdefault('total_income_sum',
                       total_income_sum['total_income_sum'])
    context.setdefault('categories', service_list_metadata(services))

    kits = ProductKit.objects.all()
    # Verify availability
    kit_alerts = 0
    for kit in kits:
        kit.available = True
        elements = KitElement.objects.filter(kit=kit)
        for element in elements:
            element.product.available = convertUnit(
                element.product.unit,
                element.unit,
                element.product.computeAvailable())
            if element.product.available < element.quantity:
                kit.available = False
                kit_alerts += 1
                break

    context.setdefault('kits', kits)
    context.setdefault('kit_alerts', kit_alerts)

    return context


@login_required
def list_service(request):
    response = prepare_service_list()
    return render(request, 'services/service_list.html', response)


@login_required
def select_service(request, next, order_id):
    response = prepare_service_list(order_id)
    response.setdefault("next", next)
    response.setdefault("order_id", order_id)
    return render(request, 'services/service_select.html', response)


@login_required
def select_new_service(request, next, order_id):
    form = ServiceCreateForm()
    if request.method == 'POST':
        form = ServiceCreateForm(request.POST)
        if form.is_valid():
            service = form.save()
            return redirect(next, order_id=order_id, service_id=service.id)
    context = {
        'form': form,
        'next': next,
        'order_id': order_id,
    }
    return render(request, 'services/service_create.html', context)


@login_required
def detail_service(request, id):
    # fetch the object related to passed id
    service = get_object_or_404(Service, id=id)
    sells = ServiceTransaction.objects.filter(
        service=service).order_by('-order__created_date')
    latest_sell = sells.first()
    latest_order = None
    if latest_sell:
        latest_order = latest_sell.order
    return render(request, 'services/service_detail.html', {'service': service,
                                                            'sells': sells,
                                                            'latest_order': latest_order})


@login_required
def delete_service(request, id):
    # fetch the object related to passed id
    obj = get_object_or_404(Service, id=id)
    obj.delete()
    return redirect('list-service')
