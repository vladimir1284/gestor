from rest_framework import serializers

from inventory.models import KitElement
from services.api.serializer.service import ServiceSerializer


class KitServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = KitElement
        fields = [
            "id",
            "kit",
            "service",
        ]
