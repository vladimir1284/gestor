from django.db import models

from rent.models.lease import Contract


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
