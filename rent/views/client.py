from datetime import datetime
from datetime import timedelta

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .invoice import mail_send_invoice
from .vehicle import FILES_ICONS
from rent.forms.lease import NoteForm
from rent.forms.lease import PaymentForm
from rent.models.lease import Contract
from rent.models.lease import Due
from rent.models.lease import Lease
from rent.models.lease import LeaseDeposit
from rent.models.lease import LeaseDocument
from rent.models.lease import LesseeData
from rent.models.lease import Note
from rent.models.lease import Payment
from rent.permissions import staff_required
from rent.tools.client import compute_client_debt
from users.models import Associated


@login_required
@staff_required
def toggle_alarm(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)
    lease.notify = not lease.notify
    lease.save()
    return redirect("client-list")


def get_sorted_clients(n=None, order_by="date", exclude=True):
    # Create leases if needed
    if exclude:
        contracts = Contract.objects.exclude(stage="ended")
    else:
        contracts = Contract.objects.all()
    clients = []
    payment_dates = {}
    debt_amounts = {}
    n_active = 0
    n_processing = 0
    n_ended = 0
    rental_debt = 0
    for contract in contracts:
        client = contract.lessee
        clients.append(client)
        client.trailer = contract.trailer
        client.contract = contract
        client.unpaid_tolls = (
            True if client.contract.tolldue_set.all().filter(stage="unpaid") else False
        )

        client.tolls_amount = (
            client.contract.tolldue_set.all()
            .filter(stage="unpaid" if client.unpaid_tolls else "paid")
            .aggregate(Sum("amount"))["amount__sum"]
        )
        if contract.contract_type == "lto":
            _, client.contract.paid = contract.paid()
        payment_dates.setdefault(client.id, timezone.now())
        debt_amounts.setdefault(client.id, 0)
        if contract.stage == "active" or contract.stage == "ended":
            if contract.stage == "active":
                n_active += 1
            elif contract.stage == "ended":
                n_ended += 1
                # Calculate Days
                if contract.ended_date:
                    client.contract.days = (
                        timezone.now().date() - contract.ended_date
                    ).days
            try:
                leases = Lease.objects.filter(contract=contract)
                lease = leases[0]
            except (Lease.DoesNotExist, IndexError):
                lease = Lease.objects.create(
                    contract=contract,
                    payment_amount=contract.payment_amount,
                    payment_frequency=contract.payment_frequency,
                    event=None,
                )
            client.lease = lease
            client.debt, last_payment, client.unpaid_dues = compute_client_debt(lease)
            if client.debt > 0:
                # Discount remaining from debt
                client.debt -= lease.remaining
                client.last_payment = client.unpaid_dues[0].start
                rental_debt += client.debt
                client.overdue_days = (timezone.now() - client.last_payment).days
            else:
                client.last_payment = timezone.now()
            payment_dates[client.id] = client.last_payment
            debt_amounts[client.id] = client.debt
        elif contract.stage != "garbage":
            n_processing += 1
    # No sorting
    sorted_clients = clients
    # Sorted by most overdue first
    if order_by == "date":
        sorted_clients = sorted(clients, key=lambda client: payment_dates[client.id])
    # Sorted by most debt amount first
    if order_by == "amount":
        sorted_clients = sorted(
            clients, key=lambda client: debt_amounts[client.id], reverse=True
        )
    if n is not None:
        return sorted_clients[:n], n_active, n_processing, n_ended, rental_debt
    return sorted_clients, n_active, n_processing, n_ended, rental_debt


@login_required
def client_list(request):
    sorted_clients, n_active, n_processing, n_ended, _ = get_sorted_clients(
        exclude=False
    )
    context = {
        "clients": sorted_clients,
        "n_active": n_active,
        "n_processing": n_processing,
        "n_ended": n_ended,
    }

    return render(request, "rent/client/client_list.html", context=context)


def base_process_payment(request, lease: Lease, payment_amount=0):
    """This function ensures that all of the remaining payment is used to pay unpaid and future dues"""

    # Retrieve the remaining
    amount = lease.remaining + payment_amount

    # Create as many dues as possible
    _, _, unpaid_dues = compute_client_debt(lease)
    # Clean up debts
    due = None
    for unpaid_due in unpaid_dues:
        if amount >= lease.payment_amount:
            amount -= lease.payment_amount
            due_date = unpaid_due.start.date()
            due = Due.objects.create(
                due_date=due_date,
                amount=lease.payment_amount,
                client=lease.contract.lessee,
                lease=lease,
            )
            # Send invoice by email
            mail_send_invoice(request, lease.id, due_date.strftime("%m%d%Y"), "true")
    # Pay dues in the future
    # If lease payment_amount is 0 will create an infinite loop
    if amount >= lease.payment_amount and lease.payment_amount > 0:
        start_time = timezone.now()
        if due is not None:
            start_time = timezone.make_aware(
                datetime.combine(due.due_date, datetime.min.time()),
                pytz.timezone(settings.TIME_ZONE),
            ) + timedelta(days=1)
        occurrences = (
            []
            if lease.event is None
            # else lease.event.get_occurrences(start_time, timezone.now())
            else lease.event.occurrences_after(start_time)
        )
        for occurrence in occurrences:
            amount -= lease.payment_amount
            due_date = occurrence.start.date()
            due = Due.objects.create(
                due_date=due_date,
                amount=lease.payment_amount,
                client=lease.contract.lessee,
                lease=lease,
            )
            # Send invoice by email
            mail_send_invoice(request, lease.id, due_date.strftime("%m%d%Y"), "true")
            if amount < lease.payment_amount:
                break

    # Save back the remaining
    lease.remaining = amount
    lease.save()


@login_required
def deactivate_reminder(request, id):
    note = get_object_or_404(Note, id=id)
    note.has_reminder = False
    note.save()
    return redirect("client-detail", note.contract.lessee.id)


@login_required
def delete_note(request, id):
    note = get_object_or_404(Note, id=id)
    note.delete()
    return redirect("client-detail", note.contract.lessee.id)


@login_required
def create_note(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.contract = contract
            note.created_by = request.user
            note.save()
            # Redirect to a success page
            return redirect("client-detail", contract.lessee.id)
    else:
        form = NoteForm()
    context = {"contract": contract, "title": "Add a note", "form": form}
    return render(request, "rent/client/create_note.html", context=context)


@login_required
def client_detail(request, id):
    # Create leases if needed
    client = get_object_or_404(Associated, id=id)
    client.contract = Contract.objects.filter(stage="active").last()
    client.data = LesseeData.objects.filter(associated=client).last()
    leases = Lease.objects.filter(contract__lessee=client, contract__stage="active")

    dues = None
    for lease in leases:
        # Debt associated with this lease
        base_process_payment(request, lease)

        lease.debt, last_date, lease.unpaid_dues = compute_client_debt(lease)
        # Payments for thi lease
        payments = Payment.objects.filter(lease=lease).order_by("-date_of_payment")
        lease.total_payment = payments.aggregate(sum_amount=Sum("amount"))["sum_amount"]
        for i, payment in enumerate(reversed(payments)):
            # Dues paid by this lease
            dues = Due.objects.filter(
                lease=lease, due_date__lte=payment.date_of_payment
            ).order_by("-due_date")
            if i > 0:
                previous_date = payment.date_of_payment
                dues = dues.exclude(due_date__lte=previous_date)
            payment.dues = dues

        if len(payments) > 0:
            lease.payments = payments

        if lease.contract.contract_type == "lto":
            lease.paid, done = lease.contract.paid()
            lease.debt = lease.contract.total_amount - lease.paid
        else:
            lease.paid_dues = Due.objects.filter(lease=lease, amount__gt=0).order_by(
                "-due_date"
            )
            lease.paid = lease.paid_dues.aggregate(sum_amount=Sum("amount"))[
                "sum_amount"
            ]

        # Notes
        lease.notes = Note.objects.filter(contract=lease.contract).order_by(
            "-created_at"
        )

        for note in lease.notes:
            if note.file:
                note.icon = "assets/img/icons/" + FILES_ICONS[note.document_type]

        # Documents
        lease.documents = LeaseDocument.objects.filter(lease=lease)
        # Check for document expiration
        for document in lease.documents:
            document.icon = "assets/img/icons/" + FILES_ICONS[document.document_type]

        # Deposits
        lease.total_deposit = 0
        lease.deposits = LeaseDeposit.objects.filter(lease=lease)
        for deposit in lease.deposits:
            lease.total_deposit += deposit.amount

        lease.contract.toll_totalpaid = 0
        lease.contract.toll_totalunpaid = 0
        lease.contract.tolls = lease.contract.tolldue_set.all()

        for toll in lease.contract.tolls:
            if toll.stage == "paid":
                lease.contract.toll_totalpaid += toll.amount
            else:
                lease.contract.toll_totalunpaid += toll.amount
    print("Completed @@@@")

    context = {"client": client, "leases": leases, "dues": dues}

    return render(request, "rent/client/client_detail.html", context=context)


def process_payment(request, payment: Payment):
    # Retrieve the remaining
    base_process_payment(request, payment.lease, payment.amount)


@login_required
def detail_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    context = {
        "payment": payment,
    }
    return render(request, "rent/client/payment_detail.html", context)


@login_required
@transaction.atomic
@staff_required
def payment(request, client_id):
    client = get_object_or_404(Associated, id=client_id)

    if request.method == "POST":
        form = PaymentForm(request.POST, client=client)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = client
            payment.user = request.user
            payment.save()
            process_payment(request, payment)
            payment.save()
            # Redirect to a success page
            return redirect("client-detail", client.id)
    else:
        form = PaymentForm(client=client)

    context = {"form": form, "client": client, "title": "Rental payment"}
    return render(request, "rent/client/payment.html", context)


@login_required
@staff_required
@transaction.atomic
def revert_payment(request, id):
    payment = get_object_or_404(Payment, id=id)

    # Delete the dues created during the payment
    dues_to_delete = Due.objects.filter(
        client=payment.client, lease=payment.lease, date__gte=payment.date
    )
    dues_amount = dues_to_delete.aggregate(total=Sum("amount"))["total"]
    dues_to_delete.delete()

    # Update the remaining amount in the previous payment if applicable
    if dues_amount is None:
        dues_amount = 0
    payment.lease.remaining += float(dues_amount) - payment.amount
    payment.lease.save()

    # Delete the payment itself
    payment.delete()

    return redirect("client-detail", payment.client.id)
