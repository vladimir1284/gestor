import datetime
from utils.models import Category
from django.db import models

from utils.models import Order, Transaction
from users.models import Associated
from django.utils.translation import gettext_lazy as _
from PIL import Image


class ServiceCategory(Category):
    pass


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE)
    sell_tax = models.FloatField(blank=True, default=8.25)
    suggested_price = models.FloatField(blank=True)
    max_price = models.FloatField(blank=True)

    def __str__(self):
        return "{}-${}".format(self.name, self.suggested_price)


class Expense(models.Model):
    concept = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    associated = models.ForeignKey(Associated, blank=True, null=True,
                                   on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cost = models.FloatField(blank=True)

    def __str__(self):
        return "{}-${}".format(self.concept, self.cost)


class ServiceTransaction(Transaction):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return "{} product: {}".format(super(Transaction, self).__str__(), self.service.name)


def year_choices():
    return [(2000, "<2010")] + [(r, r) for r in range(2010, datetime.date.today().year+1)]


class Equipment(models.Model):
    class Meta:
        abstract = True

    year = models.IntegerField(_('year'), choices=year_choices())
    vin = models.CharField(max_length=50)
    note = models.TextField(blank=True)
    IMAGE_SIZE = 500
    image = models.ImageField(upload_to='images/equipment',
                              blank=True)

    def save(self, *args, **kwargs):
        super(Equipment, self).save(*args, **kwargs)
        try:
            img = Image.open(self.image.path)

            if img.height > self.IMAGE_SIZE or img.width > self.IMAGE_SIZE:
                output_size = (self.IMAGE_SIZE, self.IMAGE_SIZE)
                img.thumbnail(output_size)
            img.save(self.image.path)
        except Exception as error:
            print(error)


class Trailer(Equipment):
    cdl = models.BooleanField()
    TYPE_CHOICE = (
        ('flatbed', 'Flatbed'),
        ('3car', '3-Car Carrier'),
        ('mini5', 'Mini-5'),
        ('lowboy', 'Lowboy'),
        ('other', _('Other')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE)
    MANUFACTURER_CHOICE = (
        ('pj', 'PJ'),
        ('bigtex', 'Bigtex'),
        ('Load trail', 'Load Trail'),
        ('kaufman', 'Kaufman'),
        ('lamar', 'Lamar'),
        ('delco', 'Delco'),
        ('gatormade', 'Gatormade'),
        ('other', _('Other')),
    )
    manufacturer = models.CharField(max_length=20, choices=MANUFACTURER_CHOICE)
    AXIS_CHIOCES = [(1, 1), (2, 2)]
    axis_number = models.IntegerField(_('Axis'), choices=AXIS_CHIOCES)
    LOAD_CHOICE = (
        (7, 7000),
        (8, 8000),
        (10, 10000),
        (12, 12000)
    )
    load = models.IntegerField(_('Load Capacity'), choices=LOAD_CHOICE)


class Vehicle(Equipment):
    MANUFACTURER_CHOICE = (
        ('ram', 'RAM'),
        ('ford', 'Ford'),
        ('chevrolet', 'Chevrolet'),
        ('gmc', 'GCM'),
        ('other', _('Other')),
    )
    manufacturer = models.CharField(max_length=20, choices=MANUFACTURER_CHOICE)
    MODEL_CHOICE = (
        ('3500', '3500'),
        ('2500', '2500'),
        ('1500', '1500'),
        ('other', _('Other')),
    )
    manufacturer = models.CharField(max_length=20, choices=MODEL_CHOICE)
    plate = models.CharField(max_length=50, blank=True)
