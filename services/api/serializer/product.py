from rest_framework import serializers

from inventory.models import Product
from inventory.models import ProductTransaction
from services.api.serializer.unit import UnitSerializer


class ProductSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()
    sell_price = serializers.SerializerMethodField()
    average_cost = serializers.SerializerMethodField()
    sells_num = serializers.SerializerMethodField()
    total_sells = serializers.SerializerMethodField()

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
            # Statistics
            "sells_num",
            "total_sells",
        ]

    def get_sell_price(self, prod: Product):
        return prod.getSuggestedPrice()

    def get_average_cost(self, prod: Product):
        return prod.getCost()

    def get_sells_num(self, prod: Product):
        trans: list[ProductTransaction] = prod.producttransaction_set.all()
        return len(trans)

    def get_total_sells(self, prod: Product):
        trans: list[ProductTransaction] = prod.producttransaction_set.all()
        sells_count = [t.quantity for t in trans]
        total = float(sum(sells_count))
        return total
