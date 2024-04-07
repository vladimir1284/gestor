from datetime import datetime

from django.utils import timezone

from dashboard.dashboard.dashboard_card import DashboardCard
from gestor.views.reports import Order
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Trailer


def _resolver():
    order_storage = Order.objects.filter(position=0)
    for o in order_storage:
        if o.trailer is None:
            trailer = Trailer()
            trailer.vin = o.vin
            trailer.plate = o.plate
            trailer.type = "Client's trailer"
            o.trailer = trailer
        o.trace = o.storage_traces.order_by("-date").first()
        if o.trace:
            o.trace.time = (timezone.make_aware(
                datetime.now()) - o.trace.date).days
    return {
        "orders_storage": order_storage,
    }


def StorageCard():
    return DashboardCard(
        name="Trailers on storage",
        template="dashboard/trailer_storage.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
