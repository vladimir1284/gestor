from rest_framework import serializers

from inventory.models import Product
from services.api.serializer.unit import UnitSerializer


class ProductSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()
    sell_price = serializers.SerializerMethodField()
    average_cost = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
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
            "sell_price",
            "average_cost",
        ]

    def get_sell_price(self, prod: Product):
        return prod.getSuggestedPrice()

    def get_average_cost(self, prod: Product):
        return prod.getCost()
