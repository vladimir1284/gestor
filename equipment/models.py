import datetime
from django.db import models
from PIL import Image
from django.utils.translation import gettext_lazy as _


def year_choices():
    return [(2000, "<2010")] + [(r, r) for r in range(2010, datetime.date.today().year+1)]


class Equipment(models.Model):
    class Meta:
        abstract = True

    year = models.IntegerField(_('year'), choices=year_choices())
    vin = models.CharField(_('VIN number'), max_length=50)
    note = models.TextField(blank=True)
    IMAGE_SIZE = 500
    image = models.ImageField(upload_to='images/equipment',
                              blank=True)
    plate = models.CharField(max_length=50, blank=True)

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
    AXIS_CHIOCES = [(1, 1), (2, 2), (3, 3)]
    axis_number = models.IntegerField(
        _('Number of axles'), choices=AXIS_CHIOCES)
    LOAD_CHOICE = (
        (7, 7000),
        (8, 8000),
        (10, 10000),
        (12, 12000)
    )
    load = models.IntegerField(_('Axle load capacity'), choices=LOAD_CHOICE)


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
    model = models.CharField(max_length=20, choices=MODEL_CHOICE)
