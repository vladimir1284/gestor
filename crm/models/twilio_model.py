from django.db import models
from users.models import Associated
from django.db.models.signals import pre_save
from django.dispatch import receiver

class TwilioCall(models.Model):
    to_state = models.CharField(max_length=100)
    caller_country = models.CharField(max_length=100)
    direction = models.CharField(max_length=20)
    caller_state = models.CharField(max_length=100)
    call_sid = models.CharField(max_length=100)
    to_phone_number = models.CharField(max_length=20)
    to_country = models.CharField(max_length=100)
    call_token = models.TextField()
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
    from_state = models.CharField(max_length=100)

    associated = models.ForeignKey(Associated, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.call_sid

@receiver(pre_save, sender=TwilioCall)
def pre_save_twilio_call(sender, instance, **kwargs):
    #revisa que no en el modelo TwilioCall no haya instancia con associated_id
    if not instance.associated and instance.from_phone_number:
        from_last_8 = instance.from_phone_number[-8:]  # Obtener los últimos 8 caracteres de from_phone_number
        try: #
            associated = Associated.objects.get(phone_number__endswith=from_last_8)
            instance.associated = associated
        except Associated.DoesNotExist:
            instance.associated = None
