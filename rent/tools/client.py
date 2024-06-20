from datetime import datetime
from datetime import timedelta

import pytz
from django.conf import settings
from django.utils import timezone

from rent.models.lease import Due
from rent.models.lease import Lease


def get_start_paying_date(lease: Lease, last_due: datetime | None | bool = True):
    # Find the last due payed by the client
    if last_due is True:
        last_due = Due.objects.filter(lease=lease).last()

    if last_due is not None:
        interval_start = (
            last_due.due_date if isinstance(last_due, Due) else last_due
        ) + timedelta(days=2)
    else:
        # If the client hasn't paid, then start paying on effective date
        interval_start = lease.contract.effective_date - timedelta(days=1)
    # Make it timezone aware
    interval_start = timezone.make_aware(
        datetime.combine(interval_start, datetime.min.time()),
        pytz.timezone(settings.TIME_ZONE),
    )
    return interval_start


def compute_client_debt(lease: Lease, due_dates: list | None = None):
    if due_dates is None:
        due_dates = []
        dues = Due.objects.filter(lease=lease)
        for d in dues:
            due_dates.append(d.due_date)

    due_dates.sort(reverse=True)

    interval_start = get_start_paying_date(
        lease,
        due_dates[0] if len(due_dates) > 0 else None,
    )
    occurrences = (
        lease.event.get_occurrences(interval_start, timezone.now())
        if lease.event is not None
        else []
    )

    unpaid_dues = []
    for occurrence in occurrences:
        # paid_due = Due.objects.filter(due_date=occurrence.start.date(), lease=lease)
        if occurrence.start.date() not in due_dates:
            unpaid_dues.append(occurrence)

    n_unpaid = len(unpaid_dues)
    return n_unpaid * lease.payment_amount, interval_start, unpaid_dues
