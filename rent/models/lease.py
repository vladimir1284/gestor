from django.db import models
from django.forms import ValidationError
from .vehicle import Trailer
from users.models import Associated
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import timedelta, datetime
import pytz
from django.contrib.auth.models import User
from schedule.models import Event, Rule, Calendar
from django.conf import settings
from .vehicle import DOCUMENT_TYPES, classify_file
from django.db.models import Max, Sum


class Contract(models.Model):
    lessee = models.ForeignKey(Associated,
                               on_delete=models.CASCADE)
    trailer = models.ForeignKey(Trailer,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    STAGE_CHOICES = (
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('signed', 'Signed'),
        ('ready', 'Ready to sign'),
        ('missing', 'Missing data'),
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    trailer_location = models.TextField()
    effective_date = models.DateField()
    ended_date = models.DateField(null=True)
    payment_amount = models.IntegerField()
    service_charge = models.IntegerField(default=100)
    PERIODICITY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
    ]
    payment_frequency = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default='weekly',
    )
    security_deposit = models.IntegerField()
    contract_term = models.FloatField(default=3)  # Months
    delayed_payments = models.IntegerField(default=0)
    TYPE_CHOICES = [
        ('lto', 'Lease to own'),
        ('rent', 'Rent'),
    ]
    contract_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='rent',
    )
    total_amount = models.IntegerField(default=0)

    def __str__(self):
        return self.trailer.__str__() + " -> " + self.lessee.__str__()

    def paid(self):
        if self.contract_type == 'lto':
            paid_amount = float(Due.objects.filter(
                lease__contract=self).aggregate(
                total_amount=Sum('amount'))['total_amount'])
            return paid_amount >= self.total_amount
        return False

    class Meta:
        ordering = ('-effective_date',)


class Lease(models.Model):
    contract = models.ForeignKey(Contract,
                                 on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True,
                              on_delete=models.SET_NULL)
    notify = models.BooleanField(default=False)
    PERIODICITY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
    ]
    payment_frequency = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default='weekly',
    )
    payment_amount = models.IntegerField()
    num_due_payments = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    last_payment_cover = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    remaining = models.FloatField(default=0)

    def compute_payment_cover(self):
        PERIOD_DAYS = {'weekly': 8,
                       'biweekly': 15,
                       'monthly': 31}
        self.last_payment_cover = Due.objects.filter(lease=self).aggregate(
            max_due_date=Max('due_date'))['max_due_date']
        if self.last_payment_cover is not None:
            self.last_payment_cover += timedelta(
                days=PERIOD_DAYS[self.payment_frequency])

    def save(self, *args, **kwargs):
        STATUS_COLOR = {'weekly': 'green',
                        'biweekly': 'brown',
                        'monthly': 'blue'}
        RULES_DICT = {
            'weekly': 'Weekly',
            'biweekly': 'Biweekly',
            'monthly': 'Monthly',
        }
        start_date = self.contract.effective_date
        if self.event is not None:
            if self.last_payment_cover is not None:
                start_date = self.last_payment_cover
            self.event.delete()

        start = timezone.make_aware(datetime.combine(
            start_date, datetime.min.time()) + timedelta(hours=12),
            pytz.timezone(settings.TIME_ZONE))

        self.event = Event.objects.create(
            title=F"{self.contract.lessee.name.split()[0]} ${int(self.payment_amount)} {self.contract.trailer.manufacturer.brand_name} {self.contract.trailer.get_type_display()} ",
            start=start,
            end=self.contract.effective_date + timedelta(hours=1),
            calendar=Calendar.objects.get(slug="rental"),
            color_event=STATUS_COLOR[self.payment_frequency],
            rule=Rule.objects.get(name=RULES_DICT[self.payment_frequency])
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete events
        self.event.delete()

        # Call the parent's delete method to perform the actual deletion
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.event.title


@receiver(pre_save, sender=Contract)
def update_effective_date(sender, instance, **kwargs):
    ''' 
    Add a rule so that if the effective_date is the 31st day, it will be
    automatically changed for the 1st of the next month at instance creation
    '''
    if instance.effective_date.day == 31:
        instance.effective_date += timedelta(days=1)


# Connect the signal handler
pre_save.connect(update_effective_date, sender=Contract)


class LeaseDocument(models.Model):
    lease = models.ForeignKey(Lease,
                              on_delete=models.CASCADE,
                              related_name='lease_document')
    file = models.FileField(upload_to='documents/leases')
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return F"{self.name} ({self.lease})"

    def save(self, *args, **kwargs):
        self.document_type = classify_file(self.file.name)
        super().save(*args, **kwargs)


class LeaseDeposit(models.Model):
    lease = models.ForeignKey(Lease,
                              on_delete=models.CASCADE,
                              related_name='lease_deposit')
    date = models.DateField()
    amount = models.FloatField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return F"${self.amount} ({self.lease})"


class HandWriting(models.Model):
    lease = models.ForeignKey(Contract,
                              on_delete=models.CASCADE,
                              related_name='hand_writing')
    position = models.CharField(max_length=50)
    img = models.ImageField(upload_to='rental/signatures')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.lease.__str__() + "-" + self.position

    def get_absolute_url(self):
        return reverse('detail-contract', args=[str(self.lease.id)])


class LesseeData(models.Model):
    associated = models.ForeignKey(Associated,
                                   on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    contact_phone = PhoneNumberField()
    insurance_number = models.CharField(max_length=150, blank=True)
    insurance_file = models.FileField(
        upload_to='rental/insurances', blank=True)
    license_number = models.CharField(max_length=150)
    license_file = models.FileField(upload_to='rental/licenses', blank=True)
    client_address = models.TextField()

    def __str__(self):
        return self.associated.name


class Inspection(models.Model):
    lease = models.ForeignKey(Contract, on_delete=models.CASCADE)
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
        if self.ramp is not None and self.megaramp:
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


class Payment(models.Model):
    '''
    This model store the actual payments made by rental clients
    '''
    date_of_payment = models.DateField()
    sender_name = models.CharField(max_length=150, blank=True)
    amount = models.FloatField()
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")

    def __str__(self):
        return f"{self.client} ${self.amount} - {self.date_of_payment}"


class Due(models.Model):
    '''
    This model store the due payments taken from the amount of money 
    of a Payment instance by considering the amount and periodicity stated 
    in the contract terms
    '''
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Associated, on_delete=models.CASCADE)
    lease = models.ForeignKey(Lease, null=True,  on_delete=models.SET_NULL)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client}  ${self.amount} - {self.due_date}"
