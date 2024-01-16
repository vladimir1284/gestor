from django.db import models
from PIL import Image

from users.models import User, Associated, Company
from equipment.models import Vehicle
from rent.models.vehicle import Trailer
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


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
        ('#696cff', 'violet'),
        ('#8592a3', 'gray'),
        ('#71dd37', 'green'),
        ('#ff3e1d', 'red'),
        ('#ffab00', 'yellow'),
        ('#03c3ec', 'blue'),
        ('#233446', 'black'),
    )
    chartColor = models.CharField(
        max_length=7, default="#8592a3", choices=COLOR_CHOICE)

    ICON_SIZE = 64
    icon = models.ImageField(upload_to='images/icons',
                             blank=True)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        thumbnailField(self.icon, self.ICON_SIZE)

    def __str__(self):
        return self.name



from django.core.exceptions import ValidationError

def custom_validator(value):
    if value.isdigit():
        if not 1 <= int(value) <= 8:
            raise ValidationError('El valor debe estar entre 1 y 8.')
    elif value != 'storage':
        raise ValidationError('El valor debe ser un número entre 1 y 8 o "storage".')

class Order(models.Model):
    # There can be several products in a single order.
    STATUS_CHOICE = (
        ('pending', _('Pending')),
        ('decline', _('Decline')),
        ('approved', _('Approved')),
        ('processing', _('Processing')),
        ('complete', _('Complete')),
    )
    TYPE_CHOICE = (
        ('sell', _('Sell')),
        ('purchase', _('Purchase')),
    )
    
    POSITION_CHOICES = [(str(i), i) for i in range(1, 9)] + [('storage', 'Storage')]

    type = models.CharField(
        max_length=20, choices=TYPE_CHOICE, default='purchase')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default='pending')
    concept = models.CharField(max_length=120, default='Initial')
    note = models.TextField(blank=True)

    position = models.CharField(max_length=10,choices = POSITION_CHOICES,
        blank=True,
        null=True,
        validators=[custom_validator],
        default="storage"
    )
    invoice_data = models.TextField(blank=True)
    vin = models.CharField(max_length=5, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    associated = models.ForeignKey(Associated, blank=True, null=True,
                                   on_delete=models.SET_NULL)
    EQUIPMENT_TYPE_CHOICE = (
        ('trailer', _('Trailer')),
        ('vehicle', _('Vehicle')),
    )
    equipment_type = models.CharField(max_length=20, blank=True, null=True,
                                      choices=EQUIPMENT_TYPE_CHOICE)
    trailer = models.ForeignKey(Trailer, blank=True, null=True,
                                on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, blank=True, null=True,
                                on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, blank=True, null=True,
                                on_delete=models.SET_NULL)
    terminated_date = models.DateTimeField(blank=True, null=True)
    processing_date = models.DateTimeField(blank=True, null=True)
    discount = models.FloatField(default=0)
    quotation = models.BooleanField(default=False)
    is_initial = False

    def __str__(self):
        return f"{self.concept}  ({self.type}) {self.created_date}"

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        order = ['pending', 'processing', 'approved', 'complete', 'decline']
        return sorted(qs, key=lambda x: order.index(x.status))


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
        return self.tax/100*self.getAmount()

    def getAmount(self):
        return self.quantity*self.price


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
        ('repair', 'Repair'),
        ('rental', 'Rental'),
        ('storage', 'Storage'),
        ('other', 'Other'),
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
