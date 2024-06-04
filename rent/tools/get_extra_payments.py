from django.utils.timezone import datetime

from rent.models.lease import Due
from rent.models.lease import Lease


def reverse_extra_payments(lease: Lease):
    if lease is None:
        return

    dues = Due.objects.filter(
        due_date__gt=datetime.now().date(),
        lease=lease,
    )
    extra_payments = 0.0
    for d in dues:
        extra_payments += float(d.amount)

    lease.remaining += extra_payments
    lease.save()

    dues.delete()


def get_extra_payments(lease: Lease):
    if lease is None:
        return 0.0

    dues = Due.objects.filter(
        due_date__gt=datetime.now().date(),
        lease=lease,
    )

    extra_payments = float(lease.remaining)
    for d in dues:
        extra_payments += float(d.amount)

    return extra_payments
