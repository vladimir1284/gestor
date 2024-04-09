from django.db import models

from services.models.order_signature import OrderSignature
from users.models import Associated


class PreorderData(models.Model):
    associated = models.ForeignKey(Associated, on_delete=models.CASCADE)
    signature = models.ForeignKey(
        OrderSignature, on_delete=models.SET_NULL, null=True, blank=True
    )
