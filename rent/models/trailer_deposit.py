from django.db import models
from django.utils.timezone import datetime
from django.utils.timezone import timedelta

from rent.models.lease import Contract
from rent.models.vehicle import Trailer
from users.models import Associated


class TrailerDepositTrace(models.Model):
    trailer_deposit = models.ForeignKey(
        "TrailerDeposit", on_delete=models.CASCADE, related_name="traces"
    )
    status = models.CharField(max_length=50, blank=True, null=True)
    amount = models.FloatField()
    days = models.IntegerField(default=7)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class TrailerDeposit(models.Model):
    client = models.ForeignKey(
        Associated,
        on_delete=models.CASCADE,
        related_name="trailer_deposit",
    )
    trailer = models.ForeignKey(
        Trailer,
        on_delete=models.CASCADE,
        related_name="trailer_deposit",
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="deposits",
        null=True,
        blank=True,
    )
    date = models.DateField()
    days = models.IntegerField(default=7)
    cancelled = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    amount = models.FloatField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} ({self.lease}) [{self.trailer}]"

    @property
    def valid_until(self):
        return self.date + timedelta(days=self.days)

    @property
    def expirated(self):
        return self.valid_until < datetime.now().date()

    @property
    def traces_rev_date(self) -> list[TrailerDepositTrace]:
        return self.traces.all().order_by("-created_at")

    @property
    def invoice_num(self) -> str:
        cli_id = str(self.client.id)
        tra_id = str(self.trailer.id)
        if len(cli_id) < 6:
            cli_id = f"{self.client.id:06d}"
        if len(tra_id) < 6:
            tra_id = f"{self.trailer.id:06d}"
        return f"DOH{cli_id}-{tra_id}"


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
