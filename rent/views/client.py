from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from rent.models.lease import LesseeData, Contract, Lease, Payment, Due
from users.models import Associated
from rent.forms.lease import PaymentForm
from django.db import transaction


@login_required
def client_list(request):
    # Create leases if needed
    contracts = Contract.objects.filter(stage="active")
    clients = []
    for contract in contracts:
        client = contract.lessee
        clients.append(client)
        client.trailer = contract.trailer
        # TODO compute client debt and status
    context = {
        "clients": clients,
    }

    return render(request, "rent/client/client_list.html", context=context)


@login_required
def client_detail(request, id):
    # Create leases if needed
    client = get_object_or_404(Associated, id=id)
    client.contract = Contract.objects.filter(stage="active").last()
    client.data = LesseeData.objects.get(associated=client)
    context = {
        "client": client,
    }

    return render(request, "rent/client/client_detail.html", context=context)


def process_payment(payment: Payment):
    # Init the payment remaining
    payment.remaining = payment.amount

    # Get the remaining money from last payment
    last_payment = Payment.objects.filter(client=payment.client,
                                          lease=payment.lease).last()
    if last_payment is not None:
        payment.remaining += last_payment.remaining
        last_payment.remaining = 0
        last_payment.save()

    # Create as many dues as possible
    last_due = Due.objects.filter(client=payment.client,
                                  lease=payment.lease).last()
    if last_due is not None:
        interval_start = last_due.date
    else:
        interval_start = payment.lease.contract.effective_date

    # Get occurrences from the last due payed
    occurrences = payment.lease.event.occurrences_after(interval_start)

    while payment.remaining >= payment.lease.payment_amount:
        payment.remaining -= payment.lease.payment_amount
        print(next(occurrences).start.date())
        Due.objects.create(
            date=next(occurrences).start.date(),
            amount=payment.lease.payment_amount,
            client=payment.client,
            lease=payment.lease
        )


@login_required
@transaction.atomic
def payment(request, client_id):
    client = get_object_or_404(Associated, id=client_id)
    try:
        lease = Lease.objects.get(
            contract__lessee=client, contract__stage='active')
    except Lease.DoesNotExist:
        raise Exception("No active lease found for the client")

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.client = client
            payment.lease = lease
            payment.user = request.user
            process_payment(payment)
            payment.save()
            # Redirect to a success page
            return redirect('client-detail', client.id)
    else:
        form = PaymentForm()

    context = {
        'form': form,
        'client': client,
    }
    return render(request, 'payment.html', context)
