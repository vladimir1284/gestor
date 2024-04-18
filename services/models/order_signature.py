from django.db import models
from django.utils import timezone

from users.models import Associated
from utils.models import Order


class OrderSignature(models.Model):
    associated = models.ForeignKey(Associated, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="hand_writing",
        null=True,
    )
    position = models.CharField(max_length=50)
    img = models.ImageField(upload_to="services/signatures")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.associated.name + "-" + self.position
