from django.db import models
from .vehicle import Trailer
from users.models import Associated


class Lease(models.Model):
    lessee = models.ForeignKey(Associated,
                               on_delete=models.CASCADE,
                               related_name='lease')
    trailer = models.ForeignKey(Trailer,
                                on_delete=models.CASCADE,
                                related_name='lease_trailer')
    STAGE_CHOICES = (
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('signed', 'Signed'),
        ('ready', 'Ready to sign'),
        ('missing', 'Missing data'),
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    location = models.TextField()
    location_file = models.FileField(upload_to='rental/locations', blank=True)
    effective_date = models.DateField()
    contract_end_date = models.DateField()
    number_of_payments = models.IntegerField()
    payment_amount = models.IntegerField()
    service_charge = models.IntegerField()
    security_deposit = models.IntegerField()
    inspection_date = models.DateField()
    current_condition = models.PositiveSmallIntegerField(
        choices=((1, 'New'),
                 (2, 'Like new'),
                 (3, 'Used')),
        default=1,
    )

    def __str__(self):
        return self.trailer.__str__() + " -> " + self.lessee.__str__()

    class Meta:
        ordering = ('-effective_date',)


class ContractDocument(models.Model):
    lease = models.ForeignKey(Lease,
                              on_delete=models.CASCADE,
                              related_name='contract_document')
    document = models.FileField(
        upload_to='rental/contracts')


class HandWriting(models.Model):
    lease = models.ForeignKey(Lease,
                              on_delete=models.CASCADE,
                              related_name='hand_writing')
    position = models.CharField(max_length=50)
    img = models.ImageField(upload_to='rental/signatures')

    def __str__(self):
        return self.lease.__str__() + "-" + self.position


class LesseeData(models.Model):
    associated = models.ForeignKey(Associated,
                                   on_delete=models.CASCADE,
                                   related_name='hand_writing')
    insurance_number = models.CharField(max_length=150, blank=True)
    insurance_file = models.FileField(upload_to='rental/insurances')
    license_number = models.CharField(max_length=150, blank=True)
    license_file = models.FileField(upload_to='rental/licenses')

    def __str__(self):
        return self.name
