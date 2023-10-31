from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from rent.models.lease import LesseeData, Contract, Lease, Payment, Due
from users.models import Associated
from rent.forms.lease import PaymentForm
from django.db import transaction
from datetime import timedelta, datetime
from django.utils import timezone
import pytz
from django.conf import settings
from .invoice import mail_send_invoice
from .vehicle import FILES_ICONS
from rent.models.lease import LeaseDocument, LeaseDeposit
from django.db.models import Sum


def compute_client_debt(client: Associated, lease: Lease):
    interval_start = get_start_paying_date(client, lease)
    occurrences = lease.event.get_occurrences(interval_start,
                                              timezone.now())
    unpaid_dues = []
    for occurrence in occurrences:
        paid_due = Due.objects.filter(due_date=occurrence.start.date(),
                                      lease=lease)
        if len(paid_due) == 0:
            unpaid_dues.append(occurrence)
    n_unpaid = len(unpaid_dues)
    return n_unpaid*lease.payment_amount, interval_start, unpaid_dues


@login_required
def toggle_alarm(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)
    lease.notify = not lease.notify
    lease.save()
    return redirect('client-list')


def get_sorted_clients(n=None, order_by="date"):
    # Create leases if needed
    contracts = Contract.objects.exclude(stage="ended")
    clients = []
    payment_dates = {}
    debt_amounts = {}
    n_active = 0
    n_processing = 0
    rental_debt = 0
    for contract in contracts:
        client = contract.lessee
        clients.append(client)
        client.trailer = contract.trailer
        client.contract = contract
        if contract.contract_type == 'lto':
            client.contract.paid = contract.paid()
        payment_dates.setdefault(client.id, timezone.now())
        debt_amounts.setdefault(client.id, 0)
        if contract.stage == "active":
            n_active += 1
            try:
                lease = Lease.objects.get(contract=contract)
            except Lease.DoesNotExist:
                lease = Lease.objects.create(
                    contract=contract,
                    payment_amount=contract.payment_amount,
                    payment_frequency=contract.payment_frequency,
                    event=None,
                )
            client.lease = lease
            client.debt, last_payment, client.unpaid_dues = compute_client_debt(
                client, lease)
            if client.debt > 0:
                # Discount remaining from debt
                last_payment = Payment.objects.filter(lease=lease).last()
                if last_payment is not None:
                    client.debt -= last_payment.remaining
                client.last_payment = client.unpaid_dues[0].start
                rental_debt += client.debt
            else:
                client.last_payment = timezone.now()
            payment_dates[client.id] = client.last_payment
            debt_amounts[client.id] = client.debt
        else:
            n_processing += 1
    # No sorting
    sorted_clients = clients
    # Sorted by most overdue first
    if order_by == 'date':
        sorted_clients = sorted(
            clients, key=lambda client: payment_dates[client.id])
    # Sorted by most debt amount first
    if order_by == 'amount':
        sorted_clients = sorted(
            clients, key=lambda client: debt_amounts[client.id], reverse=True)
    if n is not None:
        return sorted_clients[:n], n_active, n_processing, rental_debt
    return sorted_clients, n_active, n_processing, rental_debt


@login_required
def client_list(request):
    sorted_clients, n_active, n_processing, _ = get_sorted_clients()
    context = {
        "clients": sorted_clients,
        "n_active": n_active,
        "n_processing": n_processing,
    }

    return render(request, "rent/client/client_list.html", context=context)


@login_required
def client_detail(request, id):
    # Create leases if needed
    client = get_object_or_404(Associated, id=id)
    client.contract = Contract.objects.filter(stage="active").last()
    client.data = LesseeData.objects.get(associated=client)
    leases = Lease.objects.filter(
        contract__lessee=client, contract__stage="active")

    total_deposit = 0
    dues = None
    for lease in leases:
        # Debt associated with this lease
        lease.debt, last_date, lease.unpaid_dues = compute_client_debt(
            client, lease)
        # Payments for thi lease
        payments = Payment.objects.filter(
            lease=lease).order_by('-date_of_payment')
        lease.total_payment = payments.aggregate(
            sum_amount=Sum('amount'))['sum_amount']
        for i, payment in enumerate(reversed(payments)):
            # Dues paid by this lease
            dues = Due.objects.filter(
                lease=lease,
                due_date__lte=payment.date_of_payment).order_by('-due_date')
            if i > 0:
                dues = dues.exclude(due_date__lte=previous_date)
            previous_date = payment.date_of_payment
            payment.dues = dues

        if len(payments) > 0:
            lease.remaining = payments[0].remaining
            lease.payments = payments
            # Get manuel dues after the last payment
            # dues = Due.objects.filter(
            #     lease=lease,
            #     due_date__gt=payment.date_of_payment).order_by('-due_date')
        else:
            lease.remaining = 0
        lease.paid_dues = Due.objects.filter(
            lease=lease).order_by('-due_date')
        lease.paid = lease.paid_dues.aggregate(
            sum_amount=Sum('amount'))['sum_amount']
        # Documents
        lease.documents = LeaseDocument.objects.filter(lease=lease)
        # Check for document expiration
        for document in lease.documents:
            document.icon = 'assets/img/icons/' + \
                FILES_ICONS[document.document_type]

        # Deposits
        lease.deposits = LeaseDeposit.objects.filter(lease=lease)
        for deposit in lease.deposits:
            total_deposit += deposit.amount

    context = {
        "client": client,
        "leases": leases,
        "dues": dues,
        "total_deposit": total_deposit,
    }

    return render(request, "rent/client/client_detail.html", context=context)


def get_start_paying_date(client: Associated, lease: Lease):
    # Find the last due payed by the client
    last_due = Due.objects.filter(client=client, lease=lease).last()
    if last_due is not None:
        interval_start = last_due.due_date + timedelta(days=2)
    else:
        # If the client hasn't paid, then start paying on effective date
        interval_start = lease.contract.effective_date - timedelta(days=1)
    # Make it timezone aware
    interval_start = timezone.make_aware(datetime.combine(
        interval_start, datetime.min.time()), pytz.timezone(settings.TIME_ZONE))
    return interval_start


def process_payment(request, payment: Payment):
    # Init the payment remaining
    payment.remaining = payment.amount

    # Get the remaining money from last payment
    last_payment = Payment.objects.filter(
        client=payment.client,
        lease=payment.lease).exclude(id=payment.id).last()
    if last_payment is not None:
        payment.remaining += last_payment.remaining
        last_payment.remaining = 0
        last_payment.save()

    # Create as many dues as possible
    # interval_start = get_start_paying_date(payment.client, payment.lease)
    _, _, unpaid_dues = compute_client_debt(payment.client, payment.lease)
    # Clean up debts
    due = None
    for unpaid_due in unpaid_dues:
        if payment.remaining >= payment.lease.payment_amount:
            payment.remaining -= payment.lease.payment_amount
            due_date = unpaid_due.start.date()
            due = Due.objects.create(
                due_date=due_date,
                amount=payment.lease.payment_amount,
                client=payment.client,
                lease=payment.lease
            )
            # Send invoice by email
            mail_send_invoice(request, payment.lease.id,
                              due_date.strftime("%m%d%Y"), "true")
    # Pay dues in the future
    if payment.remaining >= payment.lease.payment_amount:
        start_time = timezone.now()
        if due is not None:
            start_time = timezone.make_aware(datetime.combine(
                due.due_date, datetime.min.time()),
                pytz.timezone(settings.TIME_ZONE))+timedelta(days=1)
        occurrences = payment.lease.event.occurrences_after(start_time)
        for occurrence in occurrences:
            payment.remaining -= payment.lease.payment_amount
            due = Due.objects.create(
                due_date=occurrence.start.date(),
                amount=payment.lease.payment_amount,
                client=payment.client,
                lease=payment.lease
            )
            # Send invoice by email
            mail_send_invoice(request, payment.lease.id,
                              due_date.strftime("%m%d%Y"), "true")
            if payment.remaining < payment.lease.payment_amount:
                break


@login_required
def detail_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    context = {
        'payment': payment,
    }
    return render(request, 'rent/client/payment_detail.html', context)


@login_required
@transaction.atomic
def payment(request, client_id):
    client = get_object_or_404(Associated, id=client_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST, client=client)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = client
            payment.user = request.user
            payment.save()
            process_payment(request, payment)
            payment.save()
            # Redirect to a success page
            return redirect('client-detail', client.id)
    else:
        form = PaymentForm(client=client)

    context = {
        'form': form,
        'client': client,
        'title': "Rental payment"
    }
    return render(request, 'rent/client/payment.html', context)


@login_required
@transaction.atomic
def revert_payment(request, id):
    payment = get_object_or_404(Payment, id=id)

    # Delete the dues created during the payment
    dues_to_delete = Due.objects.filter(
        client=payment.client, lease=payment.lease, date__gte=payment.date)
    if dues_to_delete is not None:
        dues_amount = dues_to_delete.count() * payment.lease.payment_amount
        dues_to_delete.delete()

    # Update the remaining amount in the previous payment if applicable
    previous_payment = Payment.objects.filter(
        client=payment.client, lease=payment.lease, date__lt=payment.date).last()
    if previous_payment is not None:
        previous_payment.remaining = (
            dues_amount+payment.remaining-payment.amount)
        previous_payment.save()

    # Delete the payment itself
    payment.delete()

    return redirect('client-detail', payment.client.id)
