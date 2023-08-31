import datetime
from django.db import models

from utils.models import Order, Transaction, Category
from users.models import Associated
from django.utils.translation import gettext_lazy as _
from users.models import User

from django.urls import reverse
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()


class ServiceCategory(Category):
    pass


class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(ServiceCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    sell_tax = models.FloatField(blank=True, default=8.25)
    suggested_price = models.FloatField(blank=True)
    # Special services
    tire = models.BooleanField(default=False)  # Service associated to tires
    # Services that doesn't appear in the invoice
    internal = models.BooleanField(default=False)
    # Actions related to marketing tha should be carried out by the employee
    marketing = models.BooleanField(default=False)

    def __str__(self):
        return "{}-${}".format(self.name, self.suggested_price)


class Expense(models.Model):
    concept = models.CharField(max_length=120)
    image = models.ImageField(upload_to='images/expenses',
                              blank=True, storage=gd_storage)
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


class ServicePicture(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='service_picture')
    # image = models.ImageField(upload_to='pictures')
    image = models.ImageField(upload_to='images/services', storage=gd_storage)

    def get_absolute_url(self):
        return reverse('detail-service-order', kwargs={'id': self.order.id}) + '#gallery'


class PaymentCategory(Category):
    extra_charge = models.FloatField(default=0)


class Payment(models.Model):
    category = models.ForeignKey(PaymentCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    amount = models.FloatField(blank=True, null=True)
    extra_charge = models.FloatField(default=0)
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='service_payment')

    def __str__(self):
        name = ""
        if self.order.associated:
            name = self.order.associated.name
        return "order: {} client: {} amount: {}".format(self.order.id, name, self.amount)


class PendingPayment(models.Model):
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    amount = models.FloatField()
    created_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(PaymentCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        name = ""
        if self.client:
            name = self.client.name
        return "{} - ${}".format(name, self.amount)


class DebtStatus(models.Model):
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('cleared', _('Cleared')),
        ('lost', _('Lost'))
    ]
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES, default='pending')
    last_modified_date = models.DateField(auto_now=True)
    weeks = models.PositiveIntegerField(default=0)
    amount_due_per_week = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return "{} (${}) -> status: {}".format(self.client, self.client.debt, self.status)
