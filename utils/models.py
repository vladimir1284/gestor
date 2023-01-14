from django.db import models
from PIL import Image

from users.models import User, Associated, Company
from equipment.models import Vehicle, Trailer
from django.utils.translation import gettext_lazy as _


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
    ICON_SIZE = 64
    icon = models.ImageField(upload_to='images/icons',
                             blank=True)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        thumbnailField(self.icon, self.ICON_SIZE)

    def __str__(self):
        return self.name


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
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICE, default='purchase')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default='pending')
    concept = models.CharField(max_length=120, default='Initial')
    note = models.TextField(blank=True)
    badge = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    associated = models.ForeignKey(Associated, blank=True, null=True,
                                   on_delete=models.SET_NULL)
    trailer = models.ForeignKey(Trailer, blank=True, null=True,
                                on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, blank=True, null=True,
                                on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, blank=True, null=True,
                                on_delete=models.SET_NULL)
    terminated_date = models.DateTimeField(blank=True, null=True)
    discount = models.FloatField(default=0)

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
