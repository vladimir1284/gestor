from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from .sms import twilioSendSMS
from .transaction import reverse_transaction
from users.models import (
    Associated,
    Company,
)
from inventory.models import (
    ProductTransaction,
)
from inventory.views import (
    NotEnoughStockError,
)
from services.models import (
    ServiceTransaction,
    Order,
    Expense,
    ServicePicture,
    Payment,
    DebtStatus,
)
from services.forms import (
    DiscountForm,
    OrderCreateForm,
)
from rent.models.vehicle import Trailer
from django.utils.translation import gettext_lazy as _


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
    associates = Associated.objects.filter(
        type='client', active=True).order_by("name", "alias")
    context = {
        'associates': associates,
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
            return redirect('process-payment', id)
        elif order.status == 'complete':
            if status == 'decline':
                # Reverse stock
                transactions = ProductTransaction.objects.filter(order=order)
                for transaction in transactions:
                    reverse_transaction(transaction)

        if status == 'processing':
            twilioSendSMS(order, status)
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
    # orders = sorted(orders, key=lambda x: STATUS_ORDER.index(x.status))
    statuses = set()
    for order in orders:
        statuses.add(order.status)
        # transactions = ProductTransaction.objects.filter(order=order)
        computeOrderAmount(order)
    return {'orders': orders,
            'statuses': statuses}


def computeOrderAmount(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    transactions.satisfied = True
    services = ServiceTransaction.objects.filter(order=order)
    expenses = Expense.objects.filter(order=order)
    # Compute amount
    amount = 0
    tax = 0
    for transaction in transactions:
        transaction.satisfied = transaction.product.computeAvailable() >= 0
        if not transaction.satisfied:
            transactions.satisfied = False

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
    satisfied = transactions.satisfied
    # Order by amount
    transactions = list(transactions)
    # Costs
    parts_cost = 0
    consumable_cost = 0
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
            parts_cost += trans.getMinCost()
        elif (trans.product.type == 'consumable'):
            consumables = True
            consumable_amount += trans.amount
            consumable_tax += trans.total_tax
            if trans.cost is not None:
                consumable_cost += trans.cost
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
    order.total = order.amount+order.tax-order.discount
    consumable_total = consumable_tax+consumable_amount
    parts_total = parts_amount+parts_tax
    service_total = service_amount+service_tax
    # Compute tax percent
    tax_percent = 8.25

    # Profit
    profit = order.amount - expenses.amount - consumable_cost - parts_cost

    if order.associated:
        if order.associated.debt > 0:
            order.associated.debt_status = DebtStatus.objects.filter(
                client=order.associated)[0].status
    try:
        order.associated.phone_number = order.associated.phone_number.as_national
    except:
        pass
    return {'order': order,
            'services': services,
            'satisfied': satisfied,
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
            'consumables': consumables,
            'profit': profit}


@login_required
def detail_order(request, id):
    # Prepare the flow for creating order
    request.session['creating_order'] = None
    request.session['order_detail'] = id

    # Get data for the given order
    context = getOrderContext(id)

    # Discount
    if request.method == 'POST':
        form = DiscountForm(request.POST,
                            total=context['order'].total,
                            profit=123.4357239847)
        if form.is_valid():
            # Restore the old discount
            context['order'].total += context['order'].discount
            context['order'].discount = context['order'].total - \
                form.cleaned_data['round_to']  # Compute the new discount
            # Apply the new discount
            context['order'].total -= context['order'].discount
            context['order'].save()

    form = DiscountForm(total=context['order'].total,
                        profit=context['profit'])

    context.setdefault('form', form)

    # Pictures
    images = ServicePicture.objects.filter(order=context['order'])
    context.setdefault('images', images)

    if context['terminated']:

        # Payments
        context.setdefault(
            'payments', Payment.objects.filter(order=context['order']))

    return render(request, 'services/order_detail.html', context)
