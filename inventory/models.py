from django.db import models
import math

from utils.models import Category, Transaction
from services.models import Service
from django.utils.translation import gettext_lazy as _
from PIL import Image


class DifferentMagnitudeUnitsError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """
    pass


def convertUnit(input_unit, output_unit, value):
    iu = Unit.objects.get(name=input_unit)
    ou = Unit.objects.get(name=output_unit)
    if (iu.magnitude != ou.magnitude):
        raise DifferentMagnitudeUnitsError
    return value*iu.factor/ou.factor


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
    active = models.BooleanField(default=True)
    IMAGE_SIZE = 500
    image = models.ImageField(upload_to='images/products',
                              blank=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    TYPE_CHOICE = (
        ('part', _('Part')),
        ('consumable', _('Consumable')),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICE)
    sell_tax = models.FloatField(blank=True, default=8.25)
    suggested_price = models.FloatField(blank=True, default=30)
    min_price = models.FloatField(blank=True, default=0)
    quantity = models.FloatField(blank=True, default=0)
    stock_price = models.FloatField(blank=True, default=0)
    quantity_min = models.FloatField(blank=True, default=0)

    def getCost(self):
        average_cost = 0
        if self.quantity > 0:
            average_cost = self.stock_price/self.quantity
        return average_cost

    def getSuggestedPrice(self):
        if self.quantity > 0:
            average_cost = self.stock_price/self.quantity
            suggested = average_cost*(1+self.suggested_price/100)
            if suggested < self.min_price:
                return self.min_price
            else:
                if suggested < 20:
                    # Round to the nearest integer
                    return math.ceil(suggested)
                else:
                    # Round to the nearest greater multiple of 5
                    return math.ceil(suggested/5)*5
        else:
            return self.min_price

    def computeAvailable(self, current_transaction=None):
        # Compute the remaining products in stock
        available = self.quantity
        transactions = ProductTransaction.objects.filter(order__type="sell",
                                                         order__status="processing",
                                                         product=self)
        for trans in transactions:
            if (trans.id != current_transaction):
                available -= trans.quantity
        return available

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

    def getMinCost(self):
        return self.quantity*self.product.min_price

    def getAveCost(self):
        product_quantity = convertUnit(
            self.unit, self.product.unit, self.quantity)
        return product_quantity*self.product.getCost()


class PriceReference(models.Model):
    # Reference link for product price
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.CharField(max_length=20)
    url = models.URLField()
    price = models.FloatField()
    updated_date = models.DateField()

    def __str__(self):
        return F"{self.store} ${self.price:0.2f}"


class Stock(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Converted from transaction to product unit
    quantity = models.FloatField()
    # Calculated from transaction price and tax
    cost = models.FloatField()

    def __str__(self):
        return "{}-{}-${}".format(self.product.name, self.quantity, self.cost)


class ProductKit(models.Model):
    # A kit is a set of products that are usually included together in an order
    name = models.CharField(max_length=120, unique=True)
    category = models.ForeignKey(ProductCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class KitElement(models.Model):
    # Linking a product to a kit
    kit = models.ForeignKey(ProductKit, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=True, default=1)

    def __str__(self):
        return F"{self.product} -> {self.kit}"


class KitService(models.Model):
    # Linking a product to a kit
    kit = models.ForeignKey(ProductKit, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
