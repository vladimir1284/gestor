from django.utils import timezone
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from .transaction import handle_transaction
from .order import getOrderContext
from .sms import twilioSendSMS
from users.models import (
    Associated,
)
from inventory.models import (
    ProductTransaction,
)
from services.models import (
    Order,
    Payment,
    PaymentCategory,
    PendingPayment,
    DebtStatus,
)
from services.forms import (
    PaymentCategoryCreateForm,
    PaymentCreateForm,
)
from django.utils.translation import gettext_lazy as _
# -------------------- Payment -------------------------


@login_required
def create_payment_category(request):
    form = PaymentCategoryCreateForm()
    if request.method == 'POST':
        form = PaymentCategoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list-payment-category')
    context = {
        'form': form,
        'title': _('Create payment category')
    }
    return render(request, 'services/payment_category_create.html', context)


@login_required
def update_payment_category(request, id):
    category = get_object_or_404(PaymentCategory, id=id)
    form = PaymentCategoryCreateForm(instance=category)
    if request.method == 'POST':
        form = PaymentCategoryCreateForm(request.POST, request.FILES,
                                         instance=category)
        if form.is_valid():
            form.save()
            return redirect('list-payment-category')
    context = {
        'form': form,
        'title': _('Update payment category')
    }
    return render(request, 'services/payment_category_create.html', context)


@login_required
def list_payment_category(request):
    # fetch the object related to passed id
    categories = PaymentCategory.objects.all()
    context = {
        'object_list': categories
    }
    return render(request, 'services/payment_category_list.html', context)


@login_required
def delete_payment_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(PaymentCategory, id=id)
    category.delete()
    return redirect('list-payment-category')


@login_required
def process_payment(request, order_id):
    categories = PaymentCategory.objects.all().exclude(name='debt')

    # Create the debt category if it doesn't exists
    debt, created = PaymentCategory.objects.get_or_create(
        name='debt',
        defaults={'name': 'debt', 'icon': 'images/icons/debt.png'}
    )

    # Create a form for each category
    forms = []
    for category in categories:
        initial = {'category': category}
        forms.append(PaymentCreateForm(request.POST or None, prefix=category.name,
                                       initial=initial, auto_id=category.name+"_%s"))

    order = get_object_or_404(Order, id=order_id)
    if order.associated is not None:
        initial = {'category': debt}
        forms.append(PaymentCreateForm(request.POST or None, prefix=debt.name,
                                       initial=initial, auto_id=debt.name+"_%s"))

    if request.method == 'POST':
        valid = False
        do_save = True
        for form in forms:
            if form.is_valid():
                if form.cleaned_data['amount'] > 0:
                    payment = form.save(commit=False)
                    payment.order = order
                    payment.category = form.category
                    payment.extra_charge = payment.category.extra_charge
                    payments = Payment.objects.filter(order=order)

                    # Check for existing payment in the database
                    for pay in payments:
                        if pay.category == payment.category:
                            do_save = False
                            break
                    if do_save:
                        payment.save()  # Save if not repeated
                    valid = True

                    # Account for client's debt
                    if payment.category == debt:
                        if order.associated is not None:
                            order.associated.debt += payment.amount
                            order.associated.save()
        if valid:
            transactions = ProductTransaction.objects.filter(order=order)
            for transaction in transactions:
                handle_transaction(transaction)
            order.terminated_date = timezone.now()
            order.status = "complete"
            order.save()
            twilioSendSMS(order, order.status)
            return redirect('detail-service-order', order_id)
        else:
            return redirect('process-payment', order_id)

    context = getOrderContext(order_id)

    context.setdefault('forms', forms)
    context.setdefault('title', _('Process payment'))
    return render(request, 'services/payment_process.html', context)


@login_required
def pay_debt(request, client_id):
    categories = PaymentCategory.objects.all().exclude(name='debt')

    # Create a form for each category
    forms = []
    for category in categories:
        initial = {'category': category}
        forms.append(PaymentCreateForm(request.POST or None, prefix=category.name,
                                       initial=initial, auto_id=category.name+"_%s"))

    client = get_object_or_404(Associated, id=client_id)

    if request.method == 'POST':
        valid = False
        for form in forms:
            if form.is_valid():
                if form.cleaned_data['amount'] > 0:
                    # Check for double requests
                    if client.debt > 0:
                        payment = PendingPayment.objects.create(
                            client=client,
                            created_by=request.user,
                            amount=form.cleaned_data['amount'],
                            category=form.category)
                        # Discount debt
                        client.debt -= payment.amount
                        # Delete debt status data
                        if client.debt == 0:
                            debt_status = DebtStatus.objects.get(client=client)
                            debt_status.delete()
        client.save()
        return redirect('list-debtor')

    context = {'forms': forms,
               'client': client,
               'title': _('Pay debt ')}
    return render(request, 'services/pending_payment.html', context)


@login_required
def update_debt_status(request, client_id, status):
    debt_status = get_object_or_404(DebtStatus, client__id=client_id)
    if status == 'cleared':
        client = get_object_or_404(Associated, id=client_id)
        client.debt = 0
        client.save()
        debt_status.delete()
    else:
        debt_status.status = status
        debt_status.save()
    return redirect('list-debtor')


@login_required
def delete_payment(request, id, order_id):
    # fetch the object related to passed id
    payment = get_object_or_404(Payment, id=id)
    payment.delete()
    return redirect('detail-order', order_id)
