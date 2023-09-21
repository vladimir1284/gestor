from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from schedule.models import Calendar, Occurrence
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.db.models import F, Q
from rent.models.lease import LesseeData, Contract
from users.models import Associated


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
    context = {
        "client": client,
    }

    return render(request, "rent/client/client_detail.html", context=context)
