from django.db import models
from datetime import datetime
from django.urls import reverse
from vehicle import Trailer


class Tracker(models.Model):
    trailer = models.ForeignKey(Trailer, blank=True, null=True,
                                on_delete=models.SET_NULL)
    last_update = models.DateTimeField(blank=True, null=True)
    imei = models.IntegerField()
    device_password = models.CharField(max_length=15, default="123456")
    device_id = models.IntegerField(blank=True)

    class Modes(models.IntegerChoices):
        Keepalived = 0
        Tracking = 1
    Mode = models.IntegerField(choices=Modes.choices, default=0)
    Tint = models.IntegerField(default=60)
    TGPS = models.IntegerField(default=5)
    Tsend = models.IntegerField(default=3)

    def get_absolute_url(self):
        return reverse('tracker_detail', kwargs={'id': self.id})


class TrackerUpload(models.Model):
    tracker = models.ForeignKey(Tracker,
                                on_delete=models.CASCADE,
                                related_name='data_upload')
    timestamp = models.DateTimeField(default=datetime.now)
    sequence = models.IntegerField(blank=True, null=True)
    charging = models.BooleanField(blank=True, null=True)
    battery = models.FloatField(blank=True, null=True)
    wur = models.IntegerField(blank=True, null=True)
    wdgc = models.IntegerField(blank=True, null=True)
    SOURCES = [
        ('LTE', 'Radio base'),
        ('GPS', 'GPS data'),
    ]
    source = models.CharField(
        max_length=3,
        choices=SOURCES,
        default='LTE',
    )
    # GPS
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    precision = models.FloatField(blank=True, null=True)
    # LTE
    mcc = models.IntegerField(blank=True, null=True)
    mnc = models.IntegerField(blank=True, null=True)
    lac = models.IntegerField(blank=True, null=True)
    cellid = models.IntegerField(blank=True, null=True)
