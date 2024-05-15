# En tu archivo models.py

from django.db import models

class TwilioCall(models.Model):
    called = models.CharField(max_length=20)
    to_state = models.CharField(max_length=100)
    caller_country = models.CharField(max_length=100)
    direction = models.CharField(max_length=20)
    caller_state = models.CharField(max_length=100)
    to_zip = models.CharField(max_length=20)
    call_sid = models.CharField(max_length=100)
    to_phone_number = models.CharField(max_length=20)
    caller_zip = models.CharField(max_length=20)
    to_country = models.CharField(max_length=100)
    call_token = models.TextField()
    called_zip = models.CharField(max_length=20)
    api_version = models.CharField(max_length=20)
    called_city = models.CharField(max_length=100)
    call_status = models.CharField(max_length=20)
    from_phone_number = models.CharField(max_length=20)
    account_sid = models.CharField(max_length=100)
    called_country = models.CharField(max_length=100)
    caller_city = models.CharField(max_length=100)
    to_city = models.CharField(max_length=100)
    from_country = models.CharField(max_length=100)
    caller_phone_number = models.CharField(max_length=20)
    from_city = models.CharField(max_length=100)
    called_state = models.CharField(max_length=100)
    from_zip = models.CharField(max_length=20)
    from_state = models.CharField(max_length=100)

    def __str__(self):
        return self.call_sid
