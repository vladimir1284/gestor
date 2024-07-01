from django.db import models

class FlaggedCalls(models.Model):
    BLACKLIST = 'BL'
    PERSONAL = 'PL'
    SPAM = 'SP'  # Constante para "Número de spam/llamadas molestas"
    PERSONAL_CALL = 'PC'  # Constante para "Llamada personal"
    OTHER_REASON = 'OT'  # Constante para "Otro motivo"

    LIST_CHOICES = [
        (BLACKLIST, 'Añadir a lista negra'),
        (PERSONAL, 'Añadir a lista de llamadas personal'),
    ]
    REASON_CHOICES = [
        (SPAM, 'Número de spam/llamadas molestas'),
        (PERSONAL_CALL, 'Llamada personal'),
        (OTHER_REASON, 'Otro motivo'),
    ]

    phone_number = models.CharField(max_length=20, unique=True)
    list_type = models.CharField(max_length=2, choices=LIST_CHOICES)
    reason = models.CharField(max_length=255, choices=REASON_CHOICES)  # Actualiza aquí

    def __str__(self):
        return self.phone_number
