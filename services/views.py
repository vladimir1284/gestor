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
    SendMailForm,
)
from utils.send_mail import MailSender
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
        'title': _("Add service"),
        'create': True,
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
        'title': _("Update Transaction"),
        'create': False,
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


def prepare_service_list(order_id):
    services = Service.objects.all()
    products = Product.objects.filter(quantity__gt=0).order_by('name')
    # Don't include products in the current order
    transactions = ProductTransaction.objects.filter(order__id=order_id)
    products_in_order = [trans.product for trans in transactions]

    product_list = []
    for product in products:
        if product not in products_in_order:
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

# -------------------- Order ----------------------------


@login_required
def create_order(request):
    initial = {'concept': None}
    creating_order = request.session.get('creating_order')
    request.session['all_selected'] = True
    order = Order()
    if creating_order:
        client_id = request.session.get('client_id')
        if client_id:
            client = Associated.objects.get(id=client_id)
            order.associated = client

        company_id = request.session.get('company_id')
        if company_id:
            company = Company.objects.get(id=company_id)
            order.company = company

        vehicle_id = request.session.get('vehicle_id')
        if vehicle_id:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            initial = {'concept': _('Maintenance to car')}
            order.vehicle = vehicle

        trailer_id = request.session.get('trailer_id')
        if trailer_id:
            trailer = Trailer.objects.get(id=trailer_id)
            initial = {'concept': _('Maintenance to trailer')}
            order.trailer = trailer

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

            # Set the equipment type in the order
            equipment_type = request.session.get('equipment_type')
            if equipment_type:
                order.equipment_type = equipment_type

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

    context = {'form': form,
               'title': _('Create service order'),
               'order': order,
               }
    return render(request, 'services/order_create.html', context)


def cleanSession(request):
    request.session['creating_order'] = None
    request.session['client_id'] = None
    request.session['vehicle_id'] = None
    request.session['trailer_id'] = None
    request.session['company_id'] = None
    request.session['all_selected'] = None
    request.session['order_detail'] = None
    request.session['equipment_type'] = None


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
        type='client', active=True).order_by("name", "alias")
    context = {
        'associateds': associateds,
        'skip': True
    }
    order_id = request.session.get('order_detail')
    if order_id is not None:
        context['skip'] = False
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
        'order': order,
        'title': _('Update service order')
    }

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
    context = prepareListOrder(request, ('processing', 'pending'))
    context.setdefault('stage', 'Terminated')
    context.setdefault('alternative_view', 'list-service-order-terminated')
    return render(request, 'services/order_list.html', context)


@login_required
def list_terminated_order(request):
    context = prepareListOrder(request, ('complete', 'decline'))
    context.setdefault('stage', 'Active')
    context.setdefault('alternative_view', 'list-service-order')
    return render(request, 'services/order_list.html', context)


def prepareListOrder(request, status_list):
    # Prepare the flow for creating order
    cleanSession(request)
    request.session['creating_order'] = True

    # List orders
    orders = Order.objects.filter(
        type='sell', status__in=status_list).order_by('-created_date')
    orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {'orders': orders,
            'statuses': statuses}


def computeOrderAmount(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    services = ServiceTransaction.objects.filter(order=order)
    expenses = Expense.objects.filter(order=order)
    # Compute amount
    amount = 0
    tax = 0
    for transaction in transactions:
        transaction.amount = transaction.getAmount()
        amount += transaction.amount
        transaction.total_tax = transaction.getTax()
        tax += transaction.total_tax
    for service in services:
        service.amount = service.getAmount()
        amount += service.amount
        service.total_tax = service.getTax()
        tax += service.total_tax
    expenses.amount = 0
    for expense in expenses:
        expenses.amount += expense.cost
    amount += expenses.amount
    order.amount = amount
    order.tax = tax
    return (transactions, services, expenses)


def getOrderContext(id):
    order = Order.objects.get(id=id)
    (transactions, services, expenses) = computeOrderAmount(order)
    # Order by amount
    transactions = list(transactions)
    # Count consumables and parts
    consumable_amount = 0
    parts_amount = 0
    consumable_tax = 0
    parts_tax = 0
    consumables = False
    for trans in transactions:
        if (trans.product.type == 'part'):
            parts_amount += trans.amount
            parts_tax += trans.total_tax
        elif (trans.product.type == 'consumable'):
            consumables = True
            consumable_amount += trans.amount
            consumable_tax += trans.total_tax
    # Account services
    service_amount = 0
    service_tax = 0
    for service in services:
        service_amount += service.amount
        service_tax += service.total_tax
    # Terminated order
    terminated = order.status in ['decline', 'complete']
    empty = (len(services) + len(transactions)) == 0
    # Compute totals
    order.total = order.amount+order.tax
    consumable_total = consumable_tax+consumable_amount
    parts_total = parts_amount+parts_tax
    service_total = service_amount+service_tax
    # Compute tax percent
    tax_percent = 8.25

    try:
        order.associated.phone_number = order.associated.phone_number.as_national
    except:
        pass
    return {'order': order,
            'services': services,
            'service_amount': service_amount,
            'service_total': service_total,
            'service_tax': service_tax,
            'expenses': expenses,
            'expenses_amount': expenses.amount,
            'transactions': transactions,
            'consumable_amount': consumable_amount,
            'consumable_total': consumable_total,
            'consumable_tax': consumable_tax,
            'parts_amount': parts_amount,
            'parts_total': parts_total,
            'parts_tax': parts_tax,
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
    mail_address = ""
    if context['order'].associated and context['order'].associated.email:
        mail_address = context['order'].associated.email
    elif context['order'].company and context['order'].company.email:
        mail_address = context['order'].company.email

    form = SendMailForm(request.POST or None,
                        initial={'mail_address': mail_address})
    context.setdefault('form', form)
    if form.is_valid():
        sendMail(
            context, form.cleaned_data['mail_address'], form.cleaned_data['send_copy'])
    return render(request, 'services/invoice_view.html', context)


@login_required
def html_invoice(request, id):
    context = getOrderContext(id)
    return render(request, 'services/invoice_pdf.html', context)


def generate_invoice_pdf(context):
    """Generate pdf."""
    image = settings.STATICFILES_DIRS[0]+'/images/icons/TOWIT.png'
    # Render
    context.setdefault('image', image)
    html_string = render_to_string('services/invoice_pdf.html', context)
    html = HTML(string=html_string)
    main_doc = html.render(presentational_hints=True)
    return main_doc.write_pdf()


@login_required
def generate_invoice(request, id):
    context = getOrderContext(id)
    result = generate_invoice_pdf(context)

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=invoice_towit.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile() as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response


def sendMail(context, address, send_copy=False):
    invoice = generate_invoice_pdf(context)
    sender = MailSender()
    send_to = [address]
    if send_copy:
        send_to.append('towithouston@gmail.com')
    sender.gmail_send_invoice(
        send_to, invoice, context['order'], context['expenses'])


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
                                               outsource=True).order_by("name", "alias"),
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
                                               outsource=True).order_by("name", "alias"),
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
