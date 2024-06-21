from datetime import datetime

from django.utils.timezone import make_aware

from dashboard.dashboard.dashboard_card import DashboardCard
from gestor.views.reports import Order
from rbac.tools.permission_param import PermissionParam


def _resolver():
    print("Trailer storage")
    orders = (
        Order.objects.filter(
            position=0,
        ).select_related(
            "vehicle",
            "associated",
            "company",
            "trailer",
            "trailer__manufacturer",
        )
        # .exclude(status="complete")
        # .exclude(status="decline")
        .prefetch_related(
            "storage_traces",
        )
    )

    clientOwnsTriler = orders.filter(
        trailer=None,
    ).exclude(
        associated=None,
    )
    for o in clientOwnsTriler:
        traces = [t for t in o.storage_traces.all()]
        traces.sort(
            key=lambda t: t.date,
            reverse=True,
        )
        o.trace = traces[0] if len(traces) > 0 else None
        # o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    clientRentTriler = orders.exclude(
        trailer=None,
    ).exclude(
        associated=None,
    )
    for o in clientRentTriler:
        traces = [t for t in o.storage_traces.all()]
        traces.sort(
            key=lambda t: t.date,
            reverse=True,
        )
        o.trace = traces[0] if len(traces) > 0 else None
        # o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    justTriler = orders.filter(
        associated=None,
    ).exclude(
        trailer=None,
    )
    for o in justTriler:
        traces = [t for t in o.storage_traces.all()]
        traces.sort(
            key=lambda t: t.date,
            reverse=True,
        )
        o.trace = traces[0] if len(traces) > 0 else None
        # o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (make_aware(datetime.now()) - o.trace.date).days

    clientOwnsTriler = sorted(
        clientOwnsTriler,
        key=lambda x: (x.trace.time if x.trace is not None else -1),
        reverse=True,
    )
    clientRentTriler = sorted(
        clientRentTriler,
        key=lambda x: (x.trace.time if x.trace is not None else -1),
        reverse=True,
    )
    justTriler = sorted(
        justTriler,
        key=lambda x: (x.trace.time if x.trace is not None else -1),
        reverse=True,
    )

    return {
        "total": orders.count(),
        "client_owns_trailers": clientOwnsTriler,
        "client_rent_trailers": clientRentTriler,
        "just_trailers": justTriler,
    }

    # order_storage = Order.objects.filter(position=0)
    # for o in order_storage:
    #     if o.trailer is None:
    #         trailer = Trailer()
    #         trailer.vin = o.vin
    #         trailer.plate = o.plate
    #         trailer.type = "Client's trailer"
    #         o.trailer = trailer
    #     o.trace = o.storage_traces.order_by("-date").first()
    #     if o.trace:
    #         o.trace.time = (timezone.make_aware(
    #             datetime.now()) - o.trace.date).days
    # return {
    #     "orders_storage": order_storage,
    # }


def StorageCard():
    return DashboardCard(
        name="Trailers on storage",
        template="dashboard/trailer_storage.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
