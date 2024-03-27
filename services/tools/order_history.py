from collections import defaultdict

from django.db.models import Q

from inventory.models import ProductTransaction
from services.models import ServiceTransaction
from utils.models import Order


def totalPrice(elements):
    sum = 0
    for element in elements[1]:
        sum += element.price

    return sum


def order_history(
    order: Order,
    *,
    parts_filter: str = "",
    services_filter: str = "",
    parts_number: int = 1,
    services_number: int = 1,
):
    parts = defaultdict(list[ProductTransaction])
    services = defaultdict(list[ServiceTransaction])

    client = order.associated
    if client is not None:
        orders = Order.objects.filter(
            ~Q(id=order.id),
            associated=client,
        )
        for order in orders:
            transactions = ProductTransaction.objects.filter(
                order=order,
                product__name__icontains=parts_filter,
            )
            for p in transactions:
                parts[p.product.name].append(p)

            services_trans = ServiceTransaction.objects.filter(
                order=order,
                service__name__icontains=services_filter,
            )
            for s in services_trans:
                services[s.service.name].append(s)

    for k in parts.keys():
        # parts[k].sort(key=lambda x: x.order.created_date, reverse=True)
        parts[k].sort(key=lambda x: x.price, reverse=True)
    for k in services.keys():
        # services[k].sort(key=lambda x: x.order.created_date, reverse=True)
        services[k].sort(key=lambda x: x.price, reverse=True)

    partsList = sorted(
        parts.items(),
        # key=lambda item: len(item[1]),
        key=lambda item: totalPrice(item),
        reverse=True,
    )
    partsTotal = len(partsList)
    partsNumber = min(parts_number, partsTotal)
    partsList = partsList[:partsNumber]
    parts = dict(partsList)

    servicesList = sorted(
        services.items(),
        # key=lambda item: len(item[1]),
        key=lambda item: totalPrice(item),
        reverse=True,
    )
    servicesTotal = len(servicesList)
    servicesNumber = min(services_number, servicesTotal)
    servicesList = servicesList[:servicesNumber]
    services = dict(servicesList)

    return parts, partsNumber, partsTotal, services, servicesNumber, servicesTotal
