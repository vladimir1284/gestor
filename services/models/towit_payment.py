from django.db import models

from utils.models import Order


class TowitPayment(models.Model):
    amount = models.FloatField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="towit_service_payment",
    )

    def __str__(self):
        return "order: {} amount: {}".format(self.order.id, self.amount)
