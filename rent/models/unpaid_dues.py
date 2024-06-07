from django.apps import apps
from django.db import models

# DepositDiscount = apps.get_model("rent", "DepositDiscount")


class UnpaidDues(models.Model):
    discount = models.ForeignKey(
        "DepositDiscount",
        on_delete=models.CASCADE,
        related_name="unpaid_dues",
    )

    date = models.DateField()
    amount = models.FloatField()
