from rest_framework import serializers

from inventory.models import ProductTransaction
from services.api.serializer.product import ProductSerializer
from services.api.serializer.unit import UnitSerializer
from services.tools.transaction import check_transaction


class ProductTransactionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    satisfied = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductTransaction
        fields = [
            "id",
            "product",
            "unit",
            "cost",
            "done",
            "decline",
            "satisfied",
            "tax",
            "active_tax",
            "price",
            "quantity",
        ]
        read_only_fields = [
            "id",
            "product",
            "unit",
            "cost",
            "done",
            "decline",
            "satisfied",
            "tax",
            "price",
        ]

    def get_satisfied(self, trans: ProductTransaction):
        return check_transaction(trans)
