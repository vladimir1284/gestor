from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.models import User
from utils.models import Category


class RentalCostCategory(Category):
    def print(self):
        print("hello")


class RentalCost(models.Model):
    concept = models.CharField(max_length=120)
    image = models.ImageField(upload_to="images/costs", blank=True)
    note = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    date = models.DateField()
    category = models.ForeignKey(
        RentalCostCategory, blank=True, null=True, on_delete=models.SET_NULL
    )
    amount = models.FloatField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rental_created_by"
    )
    related_to = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="rental_related_to",
        verbose_name=_("Associated"),
    )

    def __str__(self):
        return "{}-${}".format(self.concept, self.amount)
