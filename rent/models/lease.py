from django.db import models
from django.forms import ValidationError
from .vehicle import Trailer
from users.models import Associated
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


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
    client_id = models.ImageField(upload_to='rental/ids', blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = PhoneNumberField(blank=True)
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

    def get_absolute_url(self):
        return reverse('detail-contract', args=[str(self.lease.id)])


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


class Inspection(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    inspection_date = models.DateField(default=timezone.now)
    main_tires_choices = (
        (4, '4'),
        (6, '6'),
        (8, '8')
    )
    number_of_main_tires = models.IntegerField(choices=main_tires_choices)
    number_of_spare_tires = models.IntegerField()
    winche = models.BooleanField(default=False)
    megaramp = models.BooleanField(default=False)
    ramp_choices = (
        (None, 'None'),
        (6, '6\''),
        (8, '8\''),
        (10, '10\'')
    )
    ramp = models.IntegerField(choices=ramp_choices, null=True, blank=True)
    ramp_material_choices = (
        ('aluminum', 'Aluminum'),
        ('steel', 'Steel')
    )
    ramp_material = models.CharField(
        choices=ramp_material_choices, max_length=10, default='steel')
    note = models.TextField(null=True, blank=True)
    ancillary_battery = models.IntegerField(default=0)
    strap_4inch = models.IntegerField(default=0)

    def clean(self):
        if self.megaramp and self.ramp is not None:
            raise ValidationError("Megaramp and Ramp cannot both be selected.")
        if self.ramp is not None and not self.megaramp:
            raise ValidationError(
                "If Ramp is selected, Megaramp must be False.")


class Tire(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    position = models.IntegerField()
    type_choices = (
        ('spare', 'Spare'),
        ('main', 'Main'),
    )
    type = models.CharField(choices=type_choices, max_length=10)
    remaining_life_choices = (
        (50, '50%'),
        (60, '60%'),
        (70, '70%'),
        (80, '80%'),
        (90, '90%'),
        (100, '100%')
    )
    remaining_life = models.IntegerField(choices=remaining_life_choices,
                                         default=100)
