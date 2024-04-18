from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions.datetime import datetime
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from equipment.models import Vehicle
from rent.models.vehicle import Trailer
from services.tools.storage_reazon import getStorageReazons
from users.models import Associated
from users.models import Company
from users.models import User


def thumbnailField(image_field: models.ImageField, icon_size: int):
    try:
        img = Image.open(image_field.path)

        if img.height > icon_size or img.width > icon_size:
            output_size = (icon_size, icon_size)
            img.thumbnail(output_size)
        img.save(image_field.path)
    except Exception as error:
        print(error)


class Category(models.Model):
    class Meta:
        abstract = True

    # Categories for products
    name = models.CharField(max_length=120, unique=True)

    # Colors for the template:
    # primary (violet) #696cff
    # secondary (gray) #8592a3
    # success (green) #71dd37
    # danger (red) #ff3e1d
    # warning (yellow) #ffab00
    # info (blue) #03c3ec
    # dark (black) #233446

    COLOR_CHOICE = (
        ("#696cff", "violet"),
        ("#8592a3", "gray"),
        ("#71dd37", "green"),
        ("#ff3e1d", "red"),
        ("#ffab00", "yellow"),
        ("#03c3ec", "blue"),
        ("#233446", "black"),
    )
    chartColor = models.CharField(
        max_length=7, default="#8592a3", choices=COLOR_CHOICE)

    ICON_SIZE = 64
    icon = models.ImageField(upload_to="images/icons", blank=True)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        thumbnailField(self.icon, self.ICON_SIZE)

    def __str__(self):
        return self.name


class Order(models.Model):
    # There can be several products in a single order.
    STATUS_CHOICE = (
        ("pending", _("Pending")),
        ("decline", _("Decline")),
        ("approved", _("Approved")),
        ("processing", _("Processing")),
        ("payment_pending", _("Payment pending")),
        ("complete", _("Complete")),
    )
    TYPE_CHOICE = (
        ("sell", _("Sell")),
        ("purchase", _("Purchase")),
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICE, default="purchase")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="pending")
    concept = models.CharField(max_length=120, default="Initial")
    note = models.TextField(blank=True)
    position = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(8)],
    )
    position_date = models.DateTimeField(null=True)
    invoice_data = models.TextField(blank=True)
    # external = models.BooleanField(default=False)
    vin = models.CharField(max_length=17, blank=True, null=True)
    plate = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    associated = models.ForeignKey(
        Associated, blank=True, null=True, on_delete=models.SET_NULL
    )
    EQUIPMENT_TYPE_CHOICE = (
        ("trailer", _("Trailer")),
        ("vehicle", _("Vehicle")),
    )
    equipment_type = models.CharField(
        max_length=20, blank=True, null=True, choices=EQUIPMENT_TYPE_CHOICE
    )
    trailer = models.ForeignKey(
        Trailer, blank=True, null=True, on_delete=models.SET_NULL
    )
    vehicle = models.ForeignKey(
        Vehicle, blank=True, null=True, on_delete=models.SET_NULL
    )
    company = models.ForeignKey(
        Company, blank=True, null=True, on_delete=models.SET_NULL
    )

    terminated_date = models.DateTimeField(blank=True, null=True)
    terminated_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="terminated_orders",
    )
    processing_date = models.DateTimeField(blank=True, null=True)
    processing_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="processing_orders",
    )

    discount = models.FloatField(default=0)
    quotation = models.BooleanField(default=False)
    invoice_sended = models.BooleanField(default=False)
    is_initial = False
    storage_reason = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=getStorageReazons(),
        default="storage_service",
    )

    def __str__(self):
        return f"{self.concept}  ({self.type}) {self.created_date}"

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        order = ["pending", "processing", "approved", "complete", "decline"]
        return sorted(qs, key=lambda x: order.index(x.status))

    @property
    def last_pos_change(self):
        if self.position_date is None:
            return self.created_date
        return self.position_date

    @property
    def days_on_pos(self):
        last_pos_change = self.last_pos_change
        if last_pos_change is None:
            return -1

        return (timezone.now() - last_pos_change).days

    @property
    def external(self):
        return (
            self.associated is not None
            and self.trailer is None
            and self.company is None
        )


@receiver(models.signals.post_save, sender=Order)
def on_create(sender, instance, created, **kwargs):
    if created and instance.position == 0:
        trace = OrderTrace(
            order=instance,
            trace="storage_in",
            status=instance.status,
            reason=instance.storage_reason,
        )
        trace.save()


@receiver(models.signals.pre_save, sender=Order)
def on_field_change(sender, instance, **kwargs):
    old_order = Order.objects.filter(id=instance.id).last()
    if old_order is None:
        return

    if old_order.position != instance.position:
        if instance.position == 0:
            trace = OrderTrace(
                order=instance,
                trace="storage_in",
                status=instance.status,
                reason=instance.storage_reason,
            )
        else:
            trace = OrderTrace(
                order=instance,
                trace="storage_out",
                status=instance.status,
                reason=instance.storage_reason,
            )
        trace.save()
        instance.position_date = datetime.now()
    if instance.position == 0 and (
        old_order.status != instance.status
        or old_order.storage_reason != instance.storage_reason
    ):
        trace = OrderTrace(
            order=instance,
            trace="storage_stage",
            status=instance.status,
            reason=instance.storage_reason,
        )
        trace.save()


class OrderDeclineReazon(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    decline_reazon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    note = models.TextField(
        blank=True,
        null=True,
    )

    def get_decline_reazon(self) -> str:
        if self.decline_reazon is None:
            return "UNKNOWN"
        return str(self.decline_reazon)
        # for r in self.DECLINE_REAZON:
        #     if r[0] == self.decline_reazon:
        #         return r[1]
        # return "UNKNOWN"


class Transaction(models.Model):
    class Meta:
        abstract = True

    # Single item transaction (either sell or purchase).
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    tax = models.FloatField(default=8.25)
    price = models.FloatField()
    quantity = models.FloatField(default=1)

    def __str__(self):
        return "{}-{}-${}".format(self.order, self.quantity, self.price)

    def getTax(self):
        return self.tax / 100 * self.getAmount()

    def getAmount(self):
        return self.quantity * self.price


class Statistics(models.Model):
    """
    Weekly data associated to the date of the sunday (last day of week)
    """

    # Orders
    completed_orders = models.IntegerField(default=0)
    gross_income = models.FloatField(default=0)
    profit_before_costs = models.FloatField(default=0)
    labor_income = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    third_party = models.FloatField(default=0)
    supplies = models.FloatField(default=0)

    # Costs
    costs = models.FloatField(default=0)

    # Parts
    parts_cost = models.FloatField(default=0)
    parts_price = models.FloatField(default=0)

    # Payments
    payment_amount = models.FloatField(default=0)
    transactions = models.IntegerField(default=0)
    # Debt
    debt_created = models.FloatField(default=0)
    debt_paid = models.FloatField(default=0)

    # TOWIT
    membership_orders = models.IntegerField(default=0)
    membership_amount = models.FloatField(default=0)

    # Returned security payments
    security_payments = models.FloatField(default=0)
    returned_security_payments = models.FloatField(default=0)

    # Sunday after the week
    date = models.DateField()

    # GPT insights for the week
    gpt_insights = models.TextField(max_length=1000, blank=True, null=True)


class Plate(models.Model):
    REASON_CHOICES = [
        ("repair", "Repair"),
        ("rental", "Rental"),
        ("storage", "Storage"),
        ("other", "Other"),
    ]

    driver_name = models.CharField(max_length=100)
    incoming_date = models.DateTimeField(auto_now_add=True)
    plate = models.CharField(max_length=50, unique=True)
    outgoing_date = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.plate


class MonthlyStatistics(Statistics):
    pass


class OrderTrace(models.Model):
    TRACE_TYPE = [
        ("storage_in", "Storage in"),
        ("storage_out", "Storage out"),
        ("storage_stage", "Storage stage change"),
    ]
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="storage_traces"
    )
    date = models.DateTimeField(auto_now_add=True)
    trace = models.CharField(max_length=50, choices=TRACE_TYPE)
    status = models.CharField(max_length=50)
    reason = models.CharField(max_length=20, null=True, blank=True)

    def get_reason(self):
        reazons = getStorageReazons()
        for r in reazons:
            if r[0] == self.reason:
                return r[1]
        return "UNKNOWN"
