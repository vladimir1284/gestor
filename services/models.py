import datetime
from utils.models import Category
from django.db import models

from utils.models import Order, Transaction
from users.models import Associated
from django.utils.translation import gettext_lazy as _


class ServiceCategory(Category):
    pass


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(ServiceCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    sell_tax = models.FloatField(blank=True, default=0)
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
