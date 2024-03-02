from django.db import models

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
    active = models.BooleanField(default=True)
    amount = models.FloatField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} ({self.lease}) [{self.trailer}]"
