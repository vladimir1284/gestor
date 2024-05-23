from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone


class ContractRenovation(models.Model):
    contract = models.ForeignKey(
        "Contract", on_delete=models.CASCADE, related_name="_renovations"
    )

    created_at = models.DateField(default=timezone.now)

    effective_date = models.DateField()
    renovation_term = models.IntegerField(default=3)  # In months

    @property
    def expiration_date(self) -> datetime.date:
        return self.effective_date + relativedelta(months=self.renovation_term)

    @property
    def is_expirated(self) -> bool:
        return self.expiration_date < timezone.now().date()
