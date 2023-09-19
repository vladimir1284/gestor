from django.utils import timezone
import datetime
from django.db import models
from PIL import Image
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os


def year_choices():
    return [(2000, "<2010")] + [(r, r) for r in range(2010, datetime.date.today().year+1)]


class Equipment(models.Model):
    class Meta:
        abstract = True

    year = models.IntegerField(_('year'), choices=year_choices())
    vin = models.CharField(_('VIN number'), max_length=50, unique=True)
    note = models.TextField(blank=True)
    plate = models.CharField(max_length=50, blank=True)


class Manufacturer(models.Model):
    brand_name = models.CharField(max_length=50)
    url = models.URLField()
    ICON_SIZE = 500
    icon = models.ImageField(upload_to='images/manufacturers',
                             blank=True)

    def save(self, *args, **kwargs):
        super(Manufacturer, self).save(*args, **kwargs)
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
        ('6_car', '6-Car'),
        ('3_car_w', '3-Car Wedge'),
        ('3_car_l', '3-Car Low profile'),
        ('3_car_f', '3-Car Flatbed'),
        ('mini5', 'Mini-5'),
        ('lowboy', 'Lowboy'),
        ('ez4', 'EZ-4'),
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
    pinned = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('detail-trailer', kwargs={'id': self.trailer.id}) + '#gallery'


def classify_file(filename):
    extension = os.path.splitext(filename)[1].lower()
    if extension == ".pdf":
        return "PDF"
    elif extension in [".doc", ".docx"]:
        return "DOC"
    elif extension in [".xls", ".xlsx"]:
        return "XLS"
    elif extension in [".jpg", ".jpeg", ".png", ".gif"]:
        return "IMG"
    elif extension in [".zip", ".rar", ".tar", ".gz", ".7z"]:
        return "ZIP"
    else:
        return "BIN"


class TrailerDocument(models.Model):
    DOCUMENT_TYPES = (
        ('PDF', 'PDF'),
        ('DOC', 'DOC'),
        ('XLS', 'XLS'),
        ('IMG', 'IMG'),
        ('BIN', 'BIN'),
    )

    REMAINDER_CHOICES = (
        (1, _('1 day')),
        (7, _('1 week')),
        (30, _('1 month')),
    )

    trailer = models.ForeignKey(
        'Trailer',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    file = models.FileField(upload_to='documents/trailer')
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    expiration_date = models.DateField(null=True, blank=True)
    remainder_days = models.IntegerField(
        choices=REMAINDER_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remainder_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return F"{self.name} ({self.trailer})"

    def is_expired(self):
        if self.expiration_date is not None:
            return timezone.now().date() > self.expiration_date
        return False

    def remainder(self):
        if self.remainder_date is not None:
            return timezone.now().date() > self.remainder_date
        return False

    def save(self, *args, **kwargs):
        self.document_type = classify_file(self.file.name)
        if self.remainder_days:
            self.remainder_date = self.expiration_date - \
                timezone.timedelta(days=self.remainder_days)
            if self.remainder_date < timezone.now().date():
                raise ValueError(_('Reminder date cannot be in the past.'))
        super().save(*args, **kwargs)
