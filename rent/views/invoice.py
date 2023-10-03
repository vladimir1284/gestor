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


@login_required
def invoice(request, lease_id, date, paid):
    lease = get_object_or_404(Lease, id=lease_id)
    date = datetime.strptime(date, "%m%d%Y")
    due = Due.objects.filter(lease=lease, due_date=date).last()
    context = {'date': date,
               'lease': lease,
               'due': due,
               'paid': (paid == "true")}

    return render(request, "rent/invoice/invoice_view.html", context=context)
