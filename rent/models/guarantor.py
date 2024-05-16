from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Guarantor(models.Model):
    guarantor_name = models.CharField(max_length=120)
    guarantor_license = models.CharField(max_length=50)
    guarantor_address = models.CharField(max_length=500)
    guarantor_email = models.EmailField()
    guarantor_phone_number = PhoneNumberField(
        region=settings.PHONE_NUMBER_DEFAULT_REGION,
    )
