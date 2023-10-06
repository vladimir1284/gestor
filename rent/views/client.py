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


def compute_client_debt(client: Associated, lease: Lease):
    interval_start = get_start_paying_date(client, lease)
    occurrences = lease.event.get_occurrences(interval_start,
                                              timezone.now())
    unpaid_dues = []
    for occurrence in occurrences:
        paid_due = Due.objects.filter(due_date=occurrence.start.date())
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


@login_required
def client_list(request):
    # Create leases if needed
    contracts = Contract.objects.exclude(stage="ended")
    clients = []
    payment_dates = {}
    n_active = 0
    n_processing = 0
    for contract in contracts:
        client = contract.lessee
        clients.append(client)
        client.trailer = contract.trailer
        client.contract = contract
        payment_dates.setdefault(client.id, timezone.now())
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
            client.last_payment = last_payment
            payment_dates[client.id] = last_payment
        else:
            n_processing += 1

    sorted_clients = sorted(
        clients, key=lambda client: payment_dates[client.id])
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
    for lease in leases:
        # Debt associated with this lease
        lease.debt, last_date, lease.unpaid_dues = compute_client_debt(
            client, lease)
        # Payments for thi lease
        payments = Payment.objects.filter(
            lease=lease).order_by('-date_of_payment')
        for i, payment in enumerate(payments):
            # Dues paid by this lease
            dues = Due.objects.filter(lease=payment.lease,
                                      date__gte=payment.date)
            if i > 0:
                dues = dues.exclude(date__gte=previous_date)
            else:
                lease.remaining = payment.remaining
            previous_date = payment.date
            payment.dues = dues
        lease.payments = payments

        # Documents
        lease.documents = LeaseDocument.objects.filter(lease=lease)
        # Check for document expiration
        for document in lease.documents:
            document.icon = 'assets/img/icons/' + \
                FILES_ICONS[document.document_type]

        # Deposits
        lease.deposits = LeaseDeposit.objects.filter(lease=lease)
        total_deposit = 0
        for deposit in lease.deposits:
            total_deposit += deposit.amount

    context = {
        "client": client,
        "leases": leases,
        "total_deposit": total_deposit,
    }

    return render(request, "rent/client/client_detail.html", context=context)


def get_start_paying_date(client: Associated, lease: Lease):
    # Find the last due payed by the client
    last_due = Due.objects.filter(client=client, lease=lease).last()
    if last_due is not None:
        interval_start = last_due.due_date
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
    interval_start = get_start_paying_date(payment.client, payment.lease)

    # Get occurrences from the last due payed
    occurrences = payment.lease.event.occurrences_after(interval_start)

    while payment.remaining >= payment.lease.payment_amount:
        payment.remaining -= payment.lease.payment_amount
        due_date = next(occurrences).start.date()
        Due.objects.create(
            due_date=due_date,
            amount=payment.lease.payment_amount,
            client=payment.client,
            lease=payment.lease
        )
        # Send invoice by email
        mail_send_invoice(request, payment.lease.id,
                          due_date.strftime("%m%d%Y"), "true")


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
def revert_payment(request, client_id, payment_id):
    client = get_object_or_404(Associated, id=client_id)
    payment = get_object_or_404(Payment, id=payment_id)

    # Delete the dues created during the payment
    dues_to_delete = Due.objects.filter(
        client=client, lease=payment.lease, date__gte=payment.date)
    if dues_to_delete is not None:
        dues_amount = dues_to_delete.count() * payment.lease.payment_amount
        dues_to_delete.delete()

    # Update the remaining amount in the previous payment if applicable
    previous_payment = Payment.objects.filter(
        client=client, lease=payment.lease, date__lt=payment.date).last()
    if previous_payment is not None:
        previous_payment.remaining = (
            dues_amount+payment.remaining-payment.amount)
        previous_payment.save()

    # Delete the payment itself
    payment.delete()

    return redirect('client-detail', client.id)
