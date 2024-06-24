from rest_framework import serializers

from inventory.models import KitElement
from services.api.serializer.product import ProductSerializer
from services.api.serializer.product import UnitSerializer


class KitElementSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = KitElement
        fields = [
            "id",
            "kit",
            "product",
            "unit",
            "quantity",
        ]
