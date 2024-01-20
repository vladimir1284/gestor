from rent.models.lease import Lease, Due
from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings
import pytz


def get_start_paying_date(lease: Lease):
    # Find the last due payed by the client
    last_due = Due.objects.filter(lease=lease).last()
    if last_due is not None:
        interval_start = last_due.due_date + timedelta(days=2)
    else:
        # If the client hasn't paid, then start paying on effective date
        interval_start = lease.contract.effective_date - timedelta(days=1)
    # Make it timezone aware
    interval_start = timezone.make_aware(
        datetime.combine(interval_start, datetime.min.time()),
        pytz.timezone(settings.TIME_ZONE),
    )
    return interval_start


def compute_client_debt(lease: Lease):
    interval_start = get_start_paying_date(lease)
    occurrences = lease.event.get_occurrences(interval_start, timezone.now())
    unpaid_dues = []
    for occurrence in occurrences:
        paid_due = Due.objects.filter(due_date=occurrence.start.date(), lease=lease)
        if len(paid_due) == 0:
            unpaid_dues.append(occurrence)
    n_unpaid = len(unpaid_dues)
    return n_unpaid * lease.payment_amount, interval_start, unpaid_dues
