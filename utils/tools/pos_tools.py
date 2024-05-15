from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator


def getMaxPos() -> int:
    return settings.MAX_POSITION + 1


def getPosValidator() -> list:
    return [MinValueValidator(0), MaxValueValidator(settings.MAX_POSITION)]
