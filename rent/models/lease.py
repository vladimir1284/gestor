from datetime import datetime
from datetime import timedelta

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.template.defaultfilters import default
from django.urls import reverse
from django.utils import timezone
from num2words import num2words
from phonenumber_field.modelfields import PhoneNumberField
from schedule.models import Calendar
from schedule.models import Event
from schedule.models import Rule

from .vehicle import classify_file
from .vehicle import DOCUMENT_TYPES
from .vehicle import Trailer
from rent.models.contract_renovation import ContractRenovation
from rent.models.guarantor import Guarantor
from rent.tools.contract_renovation_notification import \
    contract_renovation_notification
from rent.tools.get_conditions_last_version import get_conditions_last_version
from users.models import Associated


class Contract(models.Model):
    lessee = models.ForeignKey(Associated, on_delete=models.CASCADE)
    guarantor = models.ForeignKey(
        Guarantor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    trailer = models.ForeignKey(Trailer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    STAGE_CHOICES = (
        ("active", "Active"),
        ("ended", "Ended"),
        ("signed", "Signed"),
        ("ready", "Ready to sign"),
        ("missing", "Missing data"),
        ("garbage", "Garbage"),
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    trailer_location = models.TextField()
    effective_date = models.DateField()
    ended_date = models.DateField(null=True)
    final_debt = models.FloatField(default=0)
    payment_amount = models.IntegerField()
    service_charge = models.IntegerField(default=100)
    PERIODICITY_CHOICES = [
        ("weekly", "Weekly"),
        ("biweekly", "Biweekly"),
        ("monthly", "Monthly"),
    ]
    payment_frequency = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default="weekly",
    )
    security_deposit = models.IntegerField()
    contract_term = models.FloatField(default=3)  # Months
    renovation_term = models.IntegerField(default=3)  # Months
    delayed_payments = models.IntegerField(default=0)
    TYPE_CHOICES = [
        ("lto", "Lease to own"),
        ("rent", "Rent"),
    ]
    contract_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default="rent",
    )
    total_amount = models.IntegerField(default=0)
    template_version = models.IntegerField(null=True, blank=True)
    client_complete = models.BooleanField(null=True, blank=True)

    renovation_15_notify = models.BooleanField(default=False)
    renovation_7_notify = models.BooleanField(default=False)

    ####### Renovations #########################################
    def _notify(self, status):
        # return

        if status == "exp7":
            self.renovation_7_notify = True
            self.renovation_15_notify = True
            self.save()
        elif status == "exp15":
            self.renovation_15_notify = True
            self.save()

        contract_renovation_notification(self, status)

    def notify(self, renovation: bool = False):
        exp_in = self.expirate_in

        if renovation:
            self._notify("renovation")
        elif exp_in.days <= 7 and not self.renovation_7_notify:
            self._notify("exp7")
        elif exp_in.days <= 15 and not self.renovation_15_notify:
            self._notify("exp15")

    @property
    def renovations(self) -> list[ContractRenovation]:
        renovations = self._renovations.order_by("effective_date").all()
        num = 0
        for r in renovations:
            num += 1
            r.num = num
            r.oword_num = num2words(num, ordinal=True)
            r.word_num = num2words(num)
        return renovations

    @property
    def last_renovation(self) -> ContractRenovation | None:
        return self._renovations.order_by("-effective_date").first()

    @property
    def renovations_count(self) -> int:
        return self._renovations.count()

    @property
    def original_expiration_date(self) -> datetime.date:
        return self.effective_date + relativedelta(months=self.contract_term)

    @property
    def expiration_date(self) -> datetime.date:
        last: ContractRenovation | None = self.last_renovation
        if last is not None:
            return last.expiration_date

        return self.original_expiration_date

    @property
    def original_is_expirated(self) -> bool:
        return self.original_expiration_date < timezone.now().date()

    @property
    def is_expirated(self) -> bool:
        return self.expiration_date < timezone.now().date()

    @property
    def expirate_in(self) -> timedelta:
        exp_in = self.expiration_date - timezone.now().date()
        return exp_in

    @property
    def expirate_in_days(self):
        exp_in = self.expirate_in
        return exp_in.days

    def _renovate(self):
        while self.is_expirated:
            exp_date = self.expiration_date
            ContractRenovation.objects.create(
                contract=self,
                effective_date=exp_date,
                renovation_term=(
                    3 if self.renovation_term <= 0 else self.renovation_term
                ),
            )

        self.renovation_15_notify = False
        self.renovation_7_notify = False
        self.save()

        self.notify(renovation=True)

    def renovate(self) -> bool:
        if self.stage == "ended" or self.stage == "garbage":
            return False

        if not self.is_expirated:
            return False

        self._renovate()
        return True

    @property
    def renovation_ctx(self) -> dict:
        # self.notify()
        return {
            "renovated": self.renovate(),
            "expirate_in_days": self.expirate_in_days,
            "is_expirated": self.is_expirated,
            "renovations": self.renovations,
            "last_renovation": self.last_renovation,
            "renovations_count": self.renovations_count,
            "expiration_date": self.expiration_date,
        }

    # ------ Renovations -----------------------------------------

    # ###### Notes ###############################################
    @property
    def notes(self) -> list:
        return Note.objects.filter(contract=self).order_by("created_at")

    @property
    def grouped_notes(self) -> dict[str, list]:
        mapped_notes = {}
        notes = self.notes
        for n in notes:
            date = str(n.created_at.date())
            if date not in mapped_notes:
                mapped_notes[date] = [n]
            else:
                mapped_notes[date].append(n)
        return mapped_notes

    def push_note(self, by: User, content: str):
        Note.objects.create(
            created_by=by,
            contract=self,
            text=content,
        )

    # ------ Notes -----------------------------------------------

    def __str__(self):
        return f"({self.id}) {self.trailer} -> {self.lessee}"

    def paid(self):
        total_amount = Due.objects.filter(lease__contract=self).aggregate(
            total_amount=Sum("amount")
        )["total_amount"]
        if total_amount is not None:
            paid_amount = float(total_amount)
        else:
            paid_amount = 0
        # Add the down payment for LTO (security_deposit)
        if self.contract_type == "lto":
            if self.stage == "active":
                lease = Lease.objects.get(contract=self)
                total_deposit = LeaseDeposit.objects.filter(lease=lease).aggregate(
                    total=Sum("amount")
                )["total"]
                if total_deposit is not None:
                    paid_amount += total_deposit
            else:
                paid_amount += self.security_deposit

        return paid_amount, (paid_amount >= self.total_amount)

    def save(self, *args, **kwargs):
        if self.template_version is None or self.template_version <= 0:
            self.template_version = get_conditions_last_version(
                self.contract_type,
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-effective_date",)


class Lease(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    notify = models.BooleanField(default=False)
    PERIODICITY_CHOICES = [
        ("weekly", "Weekly"),
        ("biweekly", "Biweekly"),
        ("monthly", "Monthly"),
    ]
    payment_frequency = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default="weekly",
    )
    payment_amount = models.IntegerField()
    num_due_payments = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    last_payment_cover = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    remaining = models.FloatField(default=0)

    def compute_payment_cover(self):
        PERIOD_DAYS = {"weekly": 8, "biweekly": 15, "monthly": 31}
        self.last_payment_cover = Due.objects.filter(lease=self).aggregate(
            max_due_date=Max("due_date")
        )["max_due_date"]
        if self.last_payment_cover is not None:
            self.last_payment_cover += timedelta(
                days=PERIOD_DAYS[self.payment_frequency]
            )

    def save(self, *args, **kwargs):
        STATUS_COLOR = {"weekly": "green", "biweekly": "brown", "monthly": "blue"}
        RULES_DICT = {
            "weekly": "Weekly",
            "biweekly": "Biweekly",
            "monthly": "Monthly",
        }
        start_date = self.contract.effective_date
        if self.event is not None:
            if self.last_payment_cover is not None:
                start_date = self.last_payment_cover
            self.event.delete()

        start = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time()) + timedelta(hours=12),
            pytz.timezone(settings.TIME_ZONE),
        )

        self.event = Event.objects.create(
            title=f"{self.contract.lessee.name.split()[0]} ${int(self.payment_amount)} {self.contract.trailer.manufacturer.brand_name if self.contract.trailer is not None and self.contract.trailer.manufacturer is not None else 'UnknownTrailer'} {self.contract.trailer.get_type_display()} ",
            start=start,
            end=self.contract.effective_date + timedelta(hours=1),
            calendar=Calendar.objects.get(slug="rental"),
            color_event=STATUS_COLOR[self.payment_frequency],
            rule=Rule.objects.get(name=RULES_DICT[self.payment_frequency]),
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete events
        self.event.delete()

        # Call the parent's delete method to perform the actual deletion
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.event.title


class Note(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    has_reminder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_date = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to="documents/notes", blank=True, null=True)
    text = models.TextField(blank=True)
    document_type = models.CharField(
        max_length=3, choices=DOCUMENT_TYPES, default="BIN"
    )

    def save(self, *args, **kwargs):
        if self.file:
            self.document_type = classify_file(self.file.name)
        super().save(*args, **kwargs)


@receiver(pre_save, sender=Contract)
def update_effective_date(sender, instance, **kwargs):
    """
    Add a rule so that if the effective_date is the 31st day, it will be
    automatically changed for the 1st of the next month at instance creation
    """
    if instance.effective_date.day == 31:
        instance.effective_date += timedelta(days=1)


# Connect the signal handler
pre_save.connect(update_effective_date, sender=Contract)


class LeaseDocument(models.Model):
    lease = models.ForeignKey(
        Lease, on_delete=models.SET_NULL, null=True, related_name="lease_document"
    )
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/leases")
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.lease})"

    def save(self, *args, **kwargs):
        self.document_type = classify_file(self.file.name)
        super().save(*args, **kwargs)


class SecurityDepositDevolution(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    amount = models.FloatField(default=0)
    total_deposited_amount = models.FloatField(default=0)
    returned = models.BooleanField(default=False)
    returned_date = models.DateField(null=True)

    immediate_refund = models.BooleanField(default=False)
    reason = models.CharField(max_length=300, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    refund_date = models.DateField(null=True)

    @property
    def income(self):
        return self.total_deposited_amount - self.amount

    @property
    def returned_amount(self):
        if self.amount < 0:
            return 0
        return self.amount

    @property
    def debt_amount(self):
        if self.amount > 0:
            return 0
        return -self.amount

    @property
    def invoice_number(self):
        contract_id = self.contract.id if self.contract is not None else "000"
        client_id = (
            self.contract.lessee.id
            if self.contract is not None and self.contract.lessee is not None
            else "000"
        )

        return f"SDD{self.id}-{contract_id}{client_id}"


class LeaseDeposit(models.Model):
    lease = models.ForeignKey(
        Lease, on_delete=models.CASCADE, related_name="lease_deposit"
    )
    date = models.DateField()
    amount = models.FloatField()
    note = models.TextField(blank=True)
    on_hold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} ({self.lease})"


class HandWriting(models.Model):
    lease = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="hand_writing"
    )
    position = models.CharField(max_length=50)
    img = models.ImageField(upload_to="rental/signatures")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.lease.__str__() + "-" + self.position

    def get_absolute_url(self):
        return reverse("detail-contract", args=[str(self.lease.id)])


class LesseeData(models.Model):
    associated = models.ForeignKey(Associated, on_delete=models.CASCADE)
    insurance_number = models.CharField(max_length=150, blank=True)
    insurance_file = models.FileField(upload_to="rental/insurances", blank=True)
    license_number = models.CharField(max_length=150)
    license_file = models.FileField(upload_to="rental/licenses", blank=True)
    client_address = models.TextField()

    contact_name = models.CharField(max_length=100)
    contact_phone = PhoneNumberField(region=settings.PHONE_NUMBER_DEFAULT_REGION)
    contact_file = models.FileField(
        upload_to="documents/contact", blank=True, null=True
    )

    contact2_name = models.CharField(max_length=100, null=True, blank=True)
    contact2_phone = PhoneNumberField(
        region=settings.PHONE_NUMBER_DEFAULT_REGION,
        null=True,
        blank=True,
    )
    contact2_file = models.FileField(
        upload_to="documents/contact", blank=True, null=True
    )

    contact3_name = models.CharField(max_length=100, null=True, blank=True)
    contact3_phone = PhoneNumberField(
        region=settings.PHONE_NUMBER_DEFAULT_REGION,
        null=True,
        blank=True,
    )
    contact3_file = models.FileField(
        upload_to="documents/contact", blank=True, null=True
    )

    def __str__(self):
        return self.associated.name


class Inspection(models.Model):
    lease = models.ForeignKey(Contract, on_delete=models.CASCADE)
    inspection_date = models.DateField(default=timezone.now)
    main_tires_choices = ((4, "4"), (6, "6"), (8, "8"))
    number_of_main_tires = models.IntegerField(choices=main_tires_choices)
    number_of_spare_tires = models.IntegerField()
    winche = models.BooleanField(default=False)
    megaramp = models.BooleanField(default=False)
    ramp_choices = ((None, "None"), (6, "6'"), (8, "8'"), (10, "10'"))
    ramp = models.IntegerField(choices=ramp_choices, null=True, blank=True)
    ramp_material_choices = (("aluminum", "Aluminum"), ("steel", "Steel"))
    ramp_material = models.CharField(
        choices=ramp_material_choices, max_length=10, default="steel"
    )
    note = models.TextField(null=True, blank=True)
    ancillary_battery = models.IntegerField(default=0)
    strap_4inch = models.IntegerField(default=0)

    def clean(self):
        if self.megaramp and self.ramp is not None:
            raise ValidationError("Megaramp and Ramp cannot both be selected.")
        if self.ramp is not None and self.megaramp:
            raise ValidationError("If Ramp is selected, Megaramp must be False.")

    def __str__(self) -> str:
        return f"{self.lease} ({self.id})"


class Tire(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    position = models.IntegerField()
    type_choices = (
        ("spare", "Spare"),
        ("main", "Main"),
    )
    type = models.CharField(choices=type_choices, max_length=10)
    remaining_life_choices = (
        (50, "50%"),
        (60, "60%"),
        (70, "70%"),
        (80, "80%"),
        (90, "90%"),
        (100, "100%"),
    )
    remaining_life = models.IntegerField(choices=remaining_life_choices, default=100)


class Payment(models.Model):
    """
    This model store the actual payments made by rental clients
    """

    date_of_payment = models.DateField()
    sender_name = models.CharField(max_length=150, blank=True)
    amount = models.FloatField()
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")

    def __str__(self):
        return f"{self.client} ${self.amount} - {self.date_of_payment}"


class Due(models.Model):
    """
    This model store the due payments taken from the amount of money
    of a Payment instance by considering the amount and periodicity stated
    in the contract terms
    """

    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    lease = models.ForeignKey(Lease, null=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client}  ${self.amount} - {self.due_date}"
