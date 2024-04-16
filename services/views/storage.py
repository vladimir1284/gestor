from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import datetime
from django.utils.timezone import make_aware

from services.models import Order
from utils.models import OrderDeclineReazon


@login_required
def storage(request):
    orders = (
        Order.objects.filter(
            position=0,
        )
        # .exclude(status="complete")
        # .exclude(status="decline")
    )
    total = orders.count()

    clientOwnsTriler = orders.filter(
        trailer=None,
    ).exclude(
        associated=None,
    )
    for o in clientOwnsTriler:
        o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    clientRentTriler = orders.exclude(
        trailer=None,
    ).exclude(
        associated=None,
    )
    for o in clientRentTriler:
        o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    justTriler = orders.filter(
        associated=None,
    ).exclude(
        trailer=None,
    )
    for o in justTriler:
        o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    onWorkshop = Order.objects.filter(position__in=[i for i in range(1, 9)])
    for o in onWorkshop:
        if o.terminated_date is not None:
            o.time = (make_aware(datetime.now()) - o.terminated_date).days
        if o.status == "decline":
            o.dec_reazon = OrderDeclineReazon.objects.filter(order=o).last()

    context = {
        "total": total + onWorkshop.count(),
        "client_owns_trailers": clientOwnsTriler,
        "client_rent_trailers": clientRentTriler,
        "just_trailers": justTriler,
        "workshop": onWorkshop,
    }
    return render(request, "services/storage/storage_view.html", context)
