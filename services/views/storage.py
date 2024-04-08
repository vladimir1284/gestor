from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import datetime
from django.utils.timezone import make_aware

from services.models import Order


@login_required
def storage(request):
    orders = (
        Order.objects.filter(
            position=0,
        )
        # .exclude(status="complete")
        # .exclude(status="decline")
    )

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

    context = {
        "client_owns_trailers": clientOwnsTriler,
        "client_rent_trailers": clientRentTriler,
        "just_trailers": justTriler,
    }
    return render(request, "services/storage/storage_view.html", context)
