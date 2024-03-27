from django.db import models
from django.utils.timezone import datetime

from rent.models.vehicle import Trailer
from users.models import Associated


class TrailerDeposit(models.Model):
    client = models.ForeignKey(
        Associated, on_delete=models.CASCADE, related_name="trailer_deposit"
    )
    trailer = models.ForeignKey(
        Trailer, on_delete=models.CASCADE, related_name="trailer_deposit"
    )
    date = models.DateField()
    cancelled = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    amount = models.FloatField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} ({self.lease}) [{self.trailer}]"


def get_active_trailers_deposit(trailer: Trailer):
    now = datetime.now()
    return TrailerDeposit.objects.filter(
        trailer=trailer, date__gte=now, cancelled=False, done=False
    )


def get_current_trailer_deposit(trailer: Trailer):
    return get_active_trailers_deposit(trailer).last()


def get_expirated_trailer_deposits(year: int, month: int):
    now = datetime.now()
    deposits = TrailerDeposit.objects.filter(
        cancelled=False,
        done=False,
        date__lt=now,
        date__year=year,
        date__month=month,
    )
    sum = 0.0
    for d in deposits:
        sum += d.amount
    return deposits, sum


def get_cancelled_trailer_deposits(year: int, month: int):
    deposits = TrailerDeposit.objects.filter(
        cancelled=True,
        date__year=year,
        date__month=month,
    )
    sum = 0.0
    for d in deposits:
        sum += d.amount
    return deposits, sum


def get_done_trailer_deposits(year: int, month: int):
    deposits = TrailerDeposit.objects.filter(
        done=True,
        date__year=year,
        date__month=month,
    )
    sum = 0.0
    for d in deposits:
        sum += d.amount
    return deposits, sum
