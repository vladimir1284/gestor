from django.db import models

from rent.models.lease import Contract
from rent.models.lease import Lease
from rent.tools.client import compute_client_debt


class DepositDiscount(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    duration = models.IntegerField(null=True, blank=True)
    location_towit = models.BooleanField(null=True, blank=True)
    location_note = models.TextField(null=True, blank=True)
    discount_trailer_cond = models.FloatField(null=True, blank=True)
    due = models.FloatField(null=True, blank=True)

    @property
    def should_return(self) -> bool:
        return self.duration == 0 and self.location_towit

    @property
    def total_discount(self) -> float:
        return float(self.due) + float(self.discount_trailer_cond)

    @property
    def debt(self) -> float:
        lease = Lease.objects.filter(contract=self.contract).last()
        if lease is None:
            return 0

        debt, last_date, unpaid_dues = compute_client_debt(lease)
        return debt

    @property
    def tolls(self) -> float:
        unpay_tolls = 0
        tolls = self.contract.tolldue_set.all()

        for toll in tolls:
            if toll.stage == "paid":
                continue

            unpay_tolls += toll.amount

        return unpay_tolls

    @property
    def total_due(self) -> float:
        return self.debt + self.tolls
