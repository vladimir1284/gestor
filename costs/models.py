from django.db import models

from utils.models import Category
from users.models import User
from django.utils.translation import gettext_lazy as _
from gdstorage.storage import GoogleDriveStorage

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()


class CostCategory(Category):
    pass


class Cost(models.Model):
    concept = models.CharField(max_length=120)
    image = models.ImageField(upload_to='images/costs',
                              blank=True, storage=gd_storage)
    note = models.TextField(blank=True)
    created_date = models.DateField(auto_now_add=True)
    date = models.DateField()
    category = models.ForeignKey(CostCategory, blank=True, null=True,
                                 on_delete=models.SET_NULL)
    amount = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='created_by')
    related_to = models.ForeignKey(User, blank=True, null=True,
                                   on_delete=models.SET_NULL,
                                   related_name='related_to',
                                   verbose_name=_('Associated'))

    def __str__(self):
        return "{}-${}".format(self.concept, self.amount)
