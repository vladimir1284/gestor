import os
from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from typing import List
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from users.models import (
    Associated,
)
from inventory.models import (
    ProductTransaction,
    Product,
    Profit as ProductProfit,
    Stock,
)
from inventory.views import (
    getTransactionAmount,
    convertUnit,
    DifferentMagnitudeUnitsError,
    NotEnoughStockError,
    prepare_product_list,
)
from utils.models import (
    Transaction,
)
from .models import (
    Service,
    ServiceTransaction,
    Profit as ServiceProfit,
    ServiceCategory,
    Order,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ServiceCreateForm,
    CategoryCreateForm,
    TransactionCreateForm,
    OrderCreateForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Category ----------------------------


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = ServiceCategory
    template_name = 'services/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(ServiceCategory, id=id)
    category.delete()
    return redirect('list-service-category')


# -------------------- Transaction ----------------------------


def renderCreateTransaction(request, form, service, order_id):
    context = {
        'form': form,
        'service': service,
        'order_id': order_id,
        'title': _("Create Transaction")
    }
    return render(request, 'services/transaction_create.html', context)


@login_required
def create_transaction(request, order_id, service_id):
    order = Order.objects.get(id=order_id)
    service = Service.objects.get(id=service_id)
    form = TransactionCreateForm()
    if request.method == 'POST':
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.service = service
            trans.save()
            return redirect('detail-service-order', id=order_id)
    return renderCreateTransaction(request, form, service, order_id)


@login_required
def update_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)

    # pass the object as instance in form
    form = TransactionCreateForm(request.POST or None,
                                 instance=transaction)

    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('detail-service-order', id=transaction.order.id)

    # add form dictionary to context
    context = {
        'form': form,
        'service': transaction.service,
        'order_id': transaction.order.id,
        'title': _("Update Transaction")
    }

    return render(request, 'services/transaction_create.html', context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)
    return render(request, 'services/transaction_detail.html', {'transaction': transaction,
                                                                'amount': getTransactionAmount(transaction)})


def handle_transaction(transaction: Transaction, order: Order):
    #  To be performed on complete orders
    if isinstance(transaction, ProductTransaction):
        product = transaction.product
        # To be used in the rest of the system
        product = Product.objects.get(id=product.id)
        product_quantity = convertUnit(
            input_unit=transaction.unit,
            output_unit=product.unit,
            value=transaction.quantity)
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
        ProductProfit.objects.create(product=product,
                                     quantity=product_quantity,
                                     profit=profit)
        product.quantity -= product_quantity
        product.stock_price -= stock_cost
        product.save()
    if isinstance(transaction, ServiceTransaction):
        pass


@login_required
def delete_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ServiceTransaction, id=id)
    transaction.delete()
    return redirect('detail-service-order', id=transaction.order.id)


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
        if service.category.name not in category_names:
            category_names.append(service.category.name)
            categories.append(service.category)
    return categories


def prepare_service_list():
    services = Service.objects.all()
    context = prepare_product_list()
    context.setdefault('services', services)
    context.setdefault('categories', service_list_metadata(services))
    return context


@login_required
def list_service(request):
    response = prepare_service_list()
    return render(request, 'services/service_list.html', response)


@login_required
def select_service(request, next, order_id):
    response = prepare_service_list()
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

# -------------------- Order ----------------------------


@login_required
def create_order(request):
    associated_id = request.session.get('associated_id')
    if associated_id is not None:
        initial = {'associated': associated_id}
    form = OrderCreateForm(initial=initial)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.type = 'sell'
            order.created_by = request.user
            order.save()
            return redirect('detail-service-order', id=order.id)
    context = {
        'form': form
    }
    return render(request, 'services/order_create.html', context)


@login_required
def select_client(request):
    if request.method == 'POST':
        next = request.GET.get('next', 'create-service-order')
        client = get_object_or_404(Associated, id=request.POST.get('id'))
        request.session['associated_id'] = client.id
        return redirect(next)
    associateds = Associated.objects.filter(
        type='client', active=True).order_by("-created_date")
    return render(request, 'services/client_list.html', {'associateds': associateds})


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)
    associated_id = request.session.get('associated_id')
    if associated_id is not None:
        associated = get_object_or_404(Associated, id=associated_id)
        order.associated = associated
    # pass the object as instance in form
    form = OrderCreateForm(instance=order)

    if request.method == 'POST':
        # pass the object as instance in form
        form = OrderCreateForm(request.POST, instance=order)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect('detail-service-order', id)

    # add form dictionary to context
    context = {
        'form': form
    }

    return render(request, 'services/order_create.html', context)


@login_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)
    order.status = status
    order.save()
    if status == 'complete':
        transactions = ProductTransaction.objects.filter(order=order)
        for transaction in transactions:
            handle_transaction(transaction, order)
    return redirect('list-service-order')


@login_required
def list_order(request):
    orders = Order.objects.filter(
        type='sell').order_by('-created_date')
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        transactions = ProductTransaction.objects.filter(order=order)
        amount = 0
        # TODO compute services
        for transaction in transactions:
            amount += getTransactionAmount(transaction)
        order.amount = amount
    return render(request, 'services/order_list.html', {'orders': orders,
                                                        'statuses': statuses})


@login_required
def detail_order(request, id):
    order = Order.objects.get(id=id)
    transactions = ProductTransaction.objects.filter(order=order)
    services = ServiceTransaction.objects.filter(order=order)
    # Compute amount
    amount = 0
    for transaction in transactions:
        transaction.amount = transaction.quantity * \
            transaction.price*(1 + transaction.tax/100.)
        amount += transaction.amount
    for service in services:
        service.amount = service.quantity * \
            service.price*(1 + service.tax/100.)
        amount += service.amount
    order.amount = amount
    # Order by amount
    transactions = list(transactions)
    transactions.sort(key=lambda trans: trans.amount, reverse=True)
    services = list(services)
    services.sort(key=lambda serv: serv.amount, reverse=True)
    # Terminated order
    terminated = order.status in ['decline', 'complete']
    empty = (len(services) + len(transactions)) == 0
    return render(request, 'services/order_detail.html', {'order': order,
                                                          'services': services,
                                                          'transactions': transactions,
                                                          'terminated': terminated,
                                                          'empty': empty})
