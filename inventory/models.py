from django.db import models

from utils.models import Category, Transaction
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image


class InventoryLocations(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProductCategory(Category):
    pass


class Unit(models.Model):
    # Unit of measurement
    name = models.CharField(max_length=120, unique=True)
    factor = models.FloatField(default=1)  # Factor to convert into SI
    MAGNITUDE_CHOICE = (
        ('mass', _('Mass')),
        ('count', _('Count')),
        ('distance', _('Distance')),
        ('volume', _('Volume')),
    )
    magnitude = models.CharField(max_length=20, choices=MAGNITUDE_CHOICE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    IMAGE_SIZE = 500
    image = models.ImageField(upload_to='images/products',
                              blank=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE)
    TYPE_CHOICE = (
        ('part', _('Part')),
        ('consumable', _('Consumable')),
    )
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICE, default='consumable')
    sell_tax = models.FloatField(blank=True, default=8.25)
    suggested_price = models.FloatField(blank=True, default=30)
    max_price = models.FloatField(blank=True, default=50)
    quantity = models.FloatField(blank=True, default=0)
    stock_price = models.FloatField(blank=True, default=0)
    quantity_min = models.FloatField(blank=True, default=0)

    def __str__(self):
        return "{}-{}-${}".format(self.name, self.quantity, self.stock_price)

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        try:
            img = Image.open(self.image.path)

            if img.height > self.IMAGE_SIZE or img.width > self.IMAGE_SIZE:
                output_size = (self.IMAGE_SIZE, self.IMAGE_SIZE)
                img.thumbnail(output_size)
            img.save(self.image.path)
        except Exception as error:
            print(error)


class ProductTransaction(Transaction):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cost = models.FloatField(blank=True, null=True)
    # As used in the transaction
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return "{} product: {}".format(super(Transaction, self).__str__(), self.product.name)


class Stock(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Converted from transaction to product unit
    quantity = models.FloatField()
    # Calculated from transaction price and tax
    cost = models.FloatField()

    def __str__(self):
        return "{}-{}-${}".format(self.product.name, self.quantity, self.cost)
