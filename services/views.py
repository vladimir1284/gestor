import os
from django.urls import reverse_lazy
from django.utils import timezone
from weasyprint import HTML
import tempfile
from django.template.loader import render_to_string
from django.http import HttpResponse
from gestor import settings
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
    Company,
)
from inventory.models import (
    ProductTransaction,
    Product,
    Stock,
)
from inventory.views import (
    getTransactionAmount,
    convertUnit,
    NotEnoughStockError,
    prepare_product_list,
)
from utils.models import (
    Transaction,
)
from .models import (
    Service,
    ServiceTransaction,
    ServiceCategory,
    Order,
    Expense,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ServiceCreateForm,
    CategoryCreateForm,
    TransactionCreateForm,
    OrderCreateForm,
    ExpenseCreateForm,
)
from equipment.models import Vehicle, Trailer
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
        'title': _("Add service")
    }
    return render(request, 'services/transaction_create.html', context)


@login_required
def create_transaction(request, order_id, service_id):
    order = Order.objects.get(id=order_id)
    service = Service.objects.get(id=service_id)
    initial = {'price': service.suggested_price}
    form = TransactionCreateForm(initial=initial)
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


def handle_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if isinstance(transaction, ProductTransaction):
        product = transaction.product
        # To be used in the rest of the system
        product = Product.objects.get(id=product.id)
        product_quantity = convertUnit(
            input_unit=transaction.unit,
            output_unit=product.unit,
            value=transaction.quantity)

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
        transaction.cost = stock_cost
        transaction.save()

        product.quantity -= product_quantity
        product.stock_price -= stock_cost
        product.save()


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
        if service.category and service.category.name not in category_names:
            category_names.append(service.category.name)
            categories.append(service.category)
    return categories


def prepare_service_list():
    services = Service.objects.all()
    products = Product.objects.filter(quantity__gt=0).order_by('name')
    product_list = []
    for product in products:
        product.available = product.computeAvailable()
        if product.available > 0:
            product_list.append(product)
    context = prepare_product_list(product_list)
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
    initial = {'concept': None}
    context = {}
    creating_order = request.session.get('creating_order')
    request.session['all_selected'] = True
    if creating_order:

        client_id = request.session.get('client_id')
        if client_id:
            client = Associated.objects.get(id=client_id)
            print(client)
            context = {'client': client}

        company_id = request.session.get('company_id')
        if company_id:
            company = Company.objects.get(id=company_id)
            context.setdefault('company', company)

        vehicle_id = request.session.get('vehicle_id')
        if vehicle_id:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            initial = {'concept': _('Maintenance to car')}
            context.setdefault('equipment', vehicle)
            context.setdefault('equipment_type', 'vehicle')

        trailer_id = request.session.get('trailer_id')
        if trailer_id:
            trailer = Trailer.objects.get(id=trailer_id)
            initial = {'concept': _('Maintenance to trailer')}
            context.setdefault('equipment', trailer)
            context.setdefault('equipment_type', 'trailer')

    form = OrderCreateForm(initial=initial)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.type = 'sell'
            order.created_by = request.user

            # Link the client to order
            client_id = request.session.get('client_id')
            if client_id:
                client = Associated.objects.get(id=client_id)
                order.associated = client

            # Link vehicle to order if exists
            vehicle_id = request.session.get('vehicle_id')
            if vehicle_id:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                order.vehicle = vehicle

            # Link trailer to order if exists
            trailer_id = request.session.get('trailer_id')
            if trailer_id:
                trailer = Trailer.objects.get(id=trailer_id)
                order.trailer = trailer

            # Link company to order if exists
            company_id = request.session.get('company_id')
            if company_id:
                company = Company.objects.get(id=company_id)
                order.company = company

            order.save()
            cleanSession(request)
            return redirect('detail-service-order', id=order.id)

    context.setdefault('form', form)
    context.setdefault('title', _('Create service order'))
    return render(request, 'services/order_create.html', context)


def cleanSession(request):
    request.session['creating_order'] = None
    request.session['client_id'] = None
    request.session['vehicle_id'] = None
    request.session['trailer_id'] = None
    request.session['company_id'] = None
    request.session['all_selected'] = None
    request.session['order_detail'] = None


@login_required
def select_client(request):
    if request.method == 'POST':
        client = get_object_or_404(Associated, id=request.POST.get('id'))
        request.session['client_id'] = client.id
        # Redirect acording to the  corresponding flow
        if request.session.get('creating_order') is not None:
            return redirect('select-company')
        else:
            order_id = request.session.get('order_detail')
            if order_id is not None:
                order = get_object_or_404(Order, id=order_id)
                order.associated = client
                order.save()
                return redirect('detail-service-order', id=order_id)

    # add form dictionary to context
    associateds = Associated.objects.filter(
        type='client', active=True).order_by("-created_date")
    context = {
        'associateds': associateds
    }
    return render(request, 'services/client_list.html', context)


@login_required
def update_order(request, id):
    # fetch the object related to passed id
    order = get_object_or_404(Order, id=id)

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
        'form': form,
        'client': order.associated,
        'title': _('Update service order')
    }
    if order.trailer:
        context.setdefault('equipment', order.trailer)
        context.setdefault('equipment_type', 'trailer')
    elif order.vehicle:
        context.setdefault('equipment', order.vehicle)
        context.setdefault('equipment_type', 'vehicle')

    return render(request, 'services/order_create.html', context)


@login_required
def update_order_status(request, id, status):
    order = get_object_or_404(Order, id=id)
    try:
        if status == 'complete':
            transactions = ProductTransaction.objects.filter(order=order)
            for transaction in transactions:
                handle_transaction(transaction)
            order.terminated_date = timezone.now()
        order.status = status
        order.save()
    except NotEnoughStockError as error:
        print(error)
    return redirect('list-service-order')


STATUS_ORDER = ['pending', 'processing', 'approved', 'complete', 'decline']


@login_required
def list_order(request):
    # Prepare the flow for creating order
    cleanSession(request)
    request.session['creating_order'] = True

    # List orders
    orders = Order.objects.filter(
        type='sell').order_by('-created_date')
    orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return render(request, 'services/order_list.html', {'orders': orders,
                                                        'statuses': statuses})


def computeOrderAmount(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    services = ServiceTransaction.objects.filter(order=order)
    expenses = Expense.objects.filter(order=order)
    # Compute amount
    amount = 0
    tax = 0
    for transaction in transactions:
        transaction.amount = computeTransactionAmount(transaction)
        amount += transaction.amount
        transaction.tax += computeTransactionTax(transaction)
        tax += transaction.tax
    for service in services:
        service.amount = computeTransactionAmount(service)
        amount += service.amount
        service.tax = computeTransactionTax(service)
        tax += service.tax
    expenses.amount = 0
    for expense in expenses:
        expenses.amount += expense.cost
        amount += expenses.amount
    order.amount = amount
    order.tax = tax
    return (transactions, services, expenses)


def computeTransactionTax(transaction: Transaction):
    return transaction.quantity * transaction.price*transaction.tax/100.


def computeTransactionAmount(transaction: Transaction):
    # *(1 + transaction.tax/100.)
    return transaction.quantity * transaction.price


def getOrderContext(id):
    order = Order.objects.get(id=id)
    (transactions, services, expenses) = computeOrderAmount(order)
    # Order by amount
    transactions = list(transactions)
    # Count consumables and parts
    consumable_amount = 0
    parts_amount = 0
    consumables = False
    for trans in transactions:
        if (trans.product.type == 'part'):
            parts_amount += trans.amount
        elif (trans.product.type == 'consumable'):
            consumables = True
            consumable_amount += trans.amount
    # Account services
    service_amount = 0
    for service in services:
        service_amount += service.amount
    # Terminated order
    terminated = order.status in ['decline', 'complete']
    empty = (len(services) + len(transactions)) == 0
    # Compute order total
    order.total = order.amount+order.tax
    # Compute tax percent
    tax_percent = 8.25
    # if order.tax > 0:
    #     tax_percent = order.tax*100/order.amount
    # Phone number format
    try:
        order.associated.phone_number = order.associated.phone_number.as_national
    except:
        pass
    return {'order': order,
            'services': services,
            'service_amount': service_amount,
            'expenses': expenses,
            'expenses_amount': expenses.amount,
            'transactions': transactions,
            'consumable_amount': consumable_amount,
            'parts_amount': parts_amount,
            'terminated': terminated,
            'empty': empty,
            'tax_percent': tax_percent,
            'consumables': consumables}


@login_required
def detail_order(request, id):
    # Prepare the flow for creating order
    request.session['creating_order'] = None
    request.session['order_detail'] = id

    # Get data for the given order
    context = getOrderContext(id)
    return render(request, 'services/order_detail.html', context)


@login_required
def view_invoice(request, id):
    context = getOrderContext(id)
    return render(request, 'services/invoice_view.html', context)


@login_required
def html_invoice(request, id):
    context = getOrderContext(id)
    return render(request, 'services/invoice_pdf.html', context)


@login_required
def generate_invoice(request, id):
    """Generate pdf."""
    image = settings.STATICFILES_DIRS[0]+'/images/icons/TOWIT.png'
    # Render
    context = getOrderContext(id)
    context.setdefault('image', image)
    html_string = render_to_string('services/invoice_pdf.html', context)
    html = HTML(string=html_string,
                base_url=request.build_absolute_uri())
    main_doc = html.render(presentational_hints=True)
    result = main_doc.write_pdf()

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=invoice_towit.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
        # # Send email
        # output.seek(0)
        # send_contract(contract, output.read(), 'contract_ready_for_signature')
        # if (stage == 3):
        #     # Store file
        #     output.seek(0)
        #     cd = ContractDocument()
        #     cd.lease = contract
        #     cd.document.save("signed_contract_%s.pdf" % id, output, True)
        #     cd.save()
        #     # # Delete handwritings
        #     # for sign in signatures:
        #     #     # os.remove(os.path.join(settings.BASE_DIR, sign.img.path))
        #     #     sign.delete()
        #     createEvent(contract, cd)

    return response

# -------------------- Expense ----------------------------


@login_required
def create_expense(request, order_id):
    associated_id = request.session.get('associated_id')
    initial = {}
    if associated_id is not None:
        initial = {'associated': associated_id}
        request.session['associated_id'] = None
    form = ExpenseCreateForm(initial=initial)
    if request.method == 'POST':
        form = ExpenseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.order = get_object_or_404(Order, id=order_id)
            expense.save()
            return redirect('detail-service-order', order_id)
    context = {
        'form': form,
        'outsource': Associated.objects.filter(type='provider',
                                               outsource=True),
        'title': _("Add third party expense")
    }
    return render(request, 'services/expense_create.html', context)


@login_required
def update_expense(request, id):
    # fetch the object related to passed id
    expense = get_object_or_404(Expense, id=id)
    associated_id = request.session.get('associated_id')
    if associated_id is not None:
        associated = get_object_or_404(Associated, id=associated_id)
        expense.associated = associated
        request.session['associated_id'] = None
    # pass the object as instance in form
    form = ExpenseCreateForm(instance=expense)

    if request.method == 'POST':
        # pass the object as instance in form
        form = ExpenseCreateForm(request.POST, request.FILES, instance=expense)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            return redirect('detail-service-order', expense.order.id)

    # add form dictionary to context
    context = {
        'form': form,
        'outsource': Associated.objects.filter(type='provider',
                                               outsource=True),
        'expense': expense,
        'title': _("Update third party expense")
    }

    return render(request, 'services/expense_create.html', context)


@login_required
def delete_expense(request, id):
    # fetch the object related to passed id
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect('detail-service-order', expense.order.id)
