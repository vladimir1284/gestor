from email.policy import default
from pyexpat import model
from django.db import models

from inventory.models import Order
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image


class ServiceCategory(models.Model):
    # Categories for products
    name = models.CharField(max_length=120, unique=True)
    ICON_SIZE = 64
    icon = models.ImageField(upload_to='images/icons',
                             blank=True)

    def save(self, *args, **kwargs):
        super(ServiceCategory, self).save(*args, **kwargs)
        try:
            img = Image.open(self.icon.path)

            if img.height > self.ICON_SIZE or img.width > self.ICON_SIZE:
                output_size = (self.ICON_SIZE, self.ICON_SIZE)
                img.thumbnail(output_size)
            img.save(self.icon.path)
        except Exception as error:
            print(error)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE)
    sell_tax = models.FloatField(blank=True, default=8.25)
    suggested_price = models.FloatField(blank=True, default=30)
    max_price = models.FloatField(blank=True, default=50)

    def __str__(self):
        return "{}-${}".format(self.name, self.suggested_price)


class Transaction(models.Model):
    # Single product transaction (either sell or purchase).
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="serviceTransaction")
    note = models.TextField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    tax = models.FloatField(default=8.25)
    price = models.FloatField()
    quantity = models.FloatField()

    def __str__(self):
        return "{}-{}-${} service: {}".format(self.order, self.quantity, self.price, self.service.name)


class Profit(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    # In product unit
    quantity = models.FloatField()
    # Calculated from sell price and inventory cost
    profit = models.FloatField()

    def __str__(self):
        return "Qty: {} profit: ${} service: {}".format(self.quantity, self.profit, self.service.name)
