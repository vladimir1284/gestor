
from django.db import models
from rent.models.vehicle import TrailerPlates
from rent.models.lease import Contract

class TollDue(models.Model):
    amount = models.IntegerField()
    plate = models.ForeignKey(TrailerPlates, on_delete=models.DO_NOTHING)
    contract = models.ForeignKey(Contract, on_delete=models.DO_NOTHING)
    STAGE_CHOICES = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid')
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    invoice = models.FileField(upload_to='toll-invoices', blank=True)
    created_date = models.DateField()

    
