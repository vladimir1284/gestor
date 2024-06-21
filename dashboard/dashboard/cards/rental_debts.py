from datetime import datetime
from datetime import time
from datetime import timedelta

from django.utils import timezone
from django.utils.dateformat import is_naive
from django.utils.dateformat import make_aware
from schedule.models.events import Event

from dashboard.dashboard.dashboard_card import DashboardCard
from rbac.tools.permission_param import PermissionParam
from rent.models.lease import Lease
from rent.views.client import compute_client_debt
from rent.views.client import get_sorted_clients


def awarize(date: datetime):
    if timezone.is_naive(date):
        date = timezone.make_aware(date, timezone.get_current_timezone())
    return date


def is_in_interval(event: Event, from_: datetime, to: datetime) -> bool:
    start = awarize(event.start)
    return start >= awarize(from_) and start <= awarize(to)


def check_interval(events: list[Event], from_: datetime, to: datetime) -> bool:
    for event in events:
        if not is_in_interval(event, from_, to):
            return True
    return False


def _resolver():
    print("rental debts")
    clients_by_date, n_active, n_processing, n_ended, rental_debt = get_sorted_clients(
        n=5
    )
    (
        clients_by_amount,
        n_active,
        n_processing,
        n_ended,
        rental_debt,
    ) = get_sorted_clients(n=5, order_by="amount")

    yesterday_dues = []

    leases = (
        Lease.objects.select_related(
            "event",
            "contract",
            "contract__lessee",
        )
        .filter(contract__stage="active")
        .prefetch_related(
            "due_set",
            "event__rule",
            "event__occurrence_set",
        )
    )

    # Get the first time of today
    first_time = datetime.combine(timezone.now().date(), time.min) - timedelta(days=1)
    # Get the last time of today
    last_time = datetime.combine(timezone.now().date(), time.max) - timedelta(days=1)

    # dues = Due.objects.select_related("lease").filter(lease__in=leases)
    # dues_map = defaultdict([])
    # for d in dues:
    #     dues_map[d.lease.id].append(d.due_date)

    for lease in leases:
        (
            debt,
            last_payment,
            unpaid_dues,
        ) = compute_client_debt(lease)
        if check_interval(unpaid_dues, first_time, last_time):
            client = lease.contract.lessee
            client.debt, client.unpaid_dues = debt, unpaid_dues
            if debt > 0:
                client.last_payment = unpaid_dues[0].start
            else:
                client.last_payment = last_payment
            yesterday_dues.append(client)
        #
        # occurrences = (
        #     []
        #     if lease.event is None
        #     else lease.event.get_occurrences(first_time, last_time)
        # )
        # if lease.id in dues_map:
        #     lease_dues = dues_map[lease.id]
        # else:
        #     lease_dues = None
        # for occurrence in occurrences:
        #     # paid_dues = Due.objects.filter(
        #     due_date=occurrence.start.date(),
        #     )
        #     # if len(paid_dues) == 0:
        #     if lease_dues is None or occurrence.start.date() not in lease_dues:
        #         client = lease.contract.lessee
        #         (
        #             client.debt,
        #             client.last_payment,
        #             client.unpaid_dues,
        #         ) = compute_client_debt(lease)
        #         if client.debt > 0:
        #             client.last_payment = client.unpaid_dues[0].start
        #         yesterday_dues.append(client)

    return {
        "rental_debt": rental_debt,
        "clients_by_date": clients_by_date,
        "clients_by_amount": clients_by_amount,
        "yesterday_dues": yesterday_dues,
    }


def RentalDebtsCard():
    return DashboardCard(
        name="Rental debt",
        template="dashboard/rental_debts.html",
        resolver=_resolver,
        self_perm=PermissionParam(""),
    )
