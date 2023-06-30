import datetime
from django.db import models
from PIL import Image
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


def year_choices():
    return [(2000, "<2010")] + [(r, r) for r in range(2010, datetime.date.today().year+1)]


class Equipment(models.Model):
    class Meta:
        abstract = True

    year = models.IntegerField(_('year'), choices=year_choices())
    vin = models.CharField(_('VIN number'), max_length=50)
    note = models.TextField(blank=True)
    plate = models.CharField(max_length=50, blank=True)


class Manufacturer(models.Model):
    brand_name = models.CharField(max_length=50)
    url = models.URLField()
    ICON_SIZE = 500
    icon = models.ImageField(upload_to='images/manufacturers',
                             blank=True)

    def save(self, *args, **kwargs):
        super(Equipment, self).save(*args, **kwargs)
        try:
            img = Image.open(self.icon.path)

            if img.height > self.ICON_SIZE or img.width > self.ICON_SIZE:
                output_size = (self.ICON_SIZE, self.ICON_SIZE)
                img.thumbnail(output_size)
            img.save(self.icon.path)
        except Exception as error:
            print(error)

    def __str__(self):
        return self.brand_name


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
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
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


class TrailerPicture(models.Model):
    trailer = models.ForeignKey(Trailer,
                                on_delete=models.CASCADE,
                                related_name='trailer_picture')
    # image = models.ImageField(upload_to='pictures')
    image = models.ImageField(upload_to='images/equipment',
                              blank=True)

    def get_absolute_url(self):
        return reverse('detail-trailer', kwargs={'id': self.trailer.id}) + '#gallery'
