from datetime import datetime
from datetime import time
from datetime import timedelta

from django.utils import timezone

from dashboard.dashboard.dashboard_card import DashboardCard
from rent.models.lease import Due
from rent.models.lease import Lease
from rent.views.client import compute_client_debt
from rent.views.client import get_sorted_clients


def _resolver():
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

    leases = Lease.objects.filter(contract__stage="active")

    # Get the first time of today
    first_time = datetime.combine(
        timezone.now().date(), time.min) - timedelta(days=1)
    # Get the last time of today
    last_time = datetime.combine(
        timezone.now().date(), time.max) - timedelta(days=1)
    for lease in leases:
        occurrences = (
            []
            if lease.event is None
            else lease.event.get_occurrences(first_time, last_time)
        )
        for occurrence in occurrences:
            paid_dues = Due.objects.filter(due_date=occurrence.start.date())
            if len(paid_dues) == 0:
                client = lease.contract.lessee
                (
                    client.debt,
                    client.last_payment,
                    client.unpaid_dues,
                ) = compute_client_debt(lease)
                if client.debt > 0:
                    client.last_payment = client.unpaid_dues[0].start
                yesterday_dues.append(client)

    return {
        "rental_debt": rental_debt,
        "clients_by_date": clients_by_date,
        "clients_by_amount": clients_by_amount,
        "yesterday_dues": yesterday_dues,
    }


def RentalDebtsCard():
    return DashboardCard(
        template="dashboard/rental_debts.html",
        resolver=_resolver,
    )
