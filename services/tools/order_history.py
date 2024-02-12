from collections import defaultdict

from django.db.models import Q
from inventory.models import ProductTransaction
from services.models import ServiceTransaction
from utils.models import Order


def order_history(order: Order):
    parts = defaultdict(list[ProductTransaction])
    services = defaultdict(list[ServiceTransaction])

    client = order.associated
    if client is not None:
        orders = Order.objects.filter(
            ~Q(id=order.id),
            associated=client,
        )
        for order in orders:
            transactions = ProductTransaction.objects.filter(order=order)
            for p in transactions:
                parts[p.product.name].append(p)

            services_trans = ServiceTransaction.objects.filter(order=order)
            for s in services_trans:
                services[s.service.name].append(s)

    for k in parts.keys():
        parts[k].sort(key=lambda x: x.order.created_date, reverse=True)
    for k in services.keys():
        services[k].sort(key=lambda x: x.order.created_date, reverse=True)

    parts = dict(
        sorted(
            parts.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )
    )
    services = dict(
        sorted(
            services.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )
    )

    return parts, services
