from email.policy import default
from pyexpat import model
from django.db import models

from users.models import User
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image


class Associated(models.Model):
    # Either client or supplier
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    avatar = models.ImageField(upload_to='images/avatars',
                               blank=True)
    phone_number = PhoneNumberField(blank=True)
    TYPE_CHOICE = (
        ('client', _('Client')),
        ('supplier', _('Supplier')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE,
                            default='client')

    def __str__(self):
        return self.name


class StoreLocations(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    # Categories for products
    name = models.CharField(max_length=120, unique=True)
    ICON_SIZE = 64
    icon = models.ImageField(upload_to='images/icons',
                             blank=True)

    def save(self, *args, **kwargs):
        super(ProductCategory, self).save(*args, **kwargs)

        img = Image.open(self.icon.path)

        if img.height > self.ICON_SIZE or img.width > self.ICON_SIZE:
            output_size = (self.ICON_SIZE, self.ICON_SIZE)
            img.thumbnail(output_size)
            img.save(self.icon.path)

    def __str__(self):
        return self.name


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
    sell_price = models.FloatField(blank=True, default=0)
    sell_tax = models.FloatField(blank=True, default=0)
    sell_price_min = models.FloatField(blank=True, default=0)
    sell_price_max = models.FloatField(blank=True, default=0)
    image = models.ImageField(upload_to='images/products',
                              blank=True)
    quantity = models.FloatField(blank=True, default=0)
    stock_price = models.FloatField(blank=True, default=0)
    quantity_min = models.FloatField(blank=True, default=0)

    def __str__(self):
        return "{}-{}-${}".format(self.name, self.quantity, self.stock_price)


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
    created_date = models.DateTimeField(auto_now_add=True)
    associated = models.ForeignKey(Associated, on_delete=models.CASCADE)

    def __str__(self):
        return self.concept


class Transaction(models.Model):
    # Single product transaction (either sell or purchase).
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tax = models.FloatField()
    price = models.FloatField()
    quantity = models.FloatField()
    # As used in the transaction
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return "{}-{}-${} product: {}".format(self.order, self.quantity, self.price, self.product.name)


class Stock(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Converted from transaction to product unit
    quantity = models.FloatField()
    # Calculated from transaction price and tax
    cost = models.FloatField()

    def __str__(self):
        return "{}-{}-${}".format(self.product.name, self.quantity, self.cost)


class Profit(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # In product unit
    quantity = models.FloatField()
    # Calculated from sell price and inventory cost
    profit = models.FloatField()

    def __str__(self):
        return "Qty: {} profit: ${} product: {}".format(self.quantity, self.profit, self.product.name)
