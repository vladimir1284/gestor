from rest_framework import serializers

from inventory.models import Product
from services.api.serializer.unit import UnitSerializer


class ProductSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()

    class Meta:
        model = Product
        fields = [
            "name",
            "active",
            "image",
            "description",
            "created_date",
            "unit",
            # "category",
            "type",
            "sell_tax",
            "suggested_price",
            "min_price",
            "quantity",
            "stock_price",
            "quantity_min",
        ]
