from django.db import models

from rent.models.lease import Contract
from rent.models.lease import Lease
from rent.models.lease import SecurityDepositDevolution
from rent.tools.client import compute_client_debt
from rent.tools.get_extra_payments import get_extra_payments


class DepositDiscount(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    duration = models.BooleanField(default=False)
    saved_duration_in_days = models.IntegerField(null=True)
    saved_contract_exp = models.DateField(null=True)

    location_towit = models.BooleanField(null=True, blank=True)
    location_note = models.TextField(null=True, blank=True)

    trailer_condition_discount = models.FloatField(default=0)

    security_deposit_devolution = models.ForeignKey(
        SecurityDepositDevolution,
        on_delete=models.CASCADE,
        null=True,
        related_name="discount",
    )

    def reset(self):
        self.expiration_date = None
        self.expirate_in_days = None
        self.save()

    @property
    def expirate_in_days(self) -> int:
        if self.saved_duration_in_days is None:
            self.saved_duration_in_days = self.contract.expirate_in_days
            self.save()
        return self.saved_duration_in_days

    @property
    def expiration_date(self):
        if self.saved_contract_exp is None:
            self.saved_contract_exp = self.contract.expiration_date
            self.save()
        return self.saved_contract_exp

    @property
    def expirate_HTML(self):
        duration = self.expirate_in_days
        days = "day" if duration == 1 or duration == -1 else "days"
        sign = "before" if duration >= 0 else "after"
        css_class = (
            ""
            # "danger" if duration < 0 else "success" if duration > 0 else "primary"
        )
        exp_date = self.expiration_date.strftime("%b %d, %Y")

        return f"""<strong>{abs(duration)}</strong>
        {days}
        <strong class="text-{css_class}">{sign}</strong>
        <strong>{exp_date}</strong>.
        """

    @property
    def should_return(self) -> bool:
        return self.duration and self.location_towit

    @property
    def total_discount(self) -> float:
        return (
            float(self.trailer_condition_discount)
            + self.debt
            + self.tolls
            - self.extra_payments
        )

    @property
    def extra_payments(self) -> float:
        lease = Lease.objects.filter(contract=self.contract).last()
        extra_payments = get_extra_payments(lease)
        return extra_payments

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
