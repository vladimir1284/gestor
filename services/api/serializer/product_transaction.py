from rest_framework import serializers

from inventory.models import ProductTransaction
from services.api.serializer.product import ProductSerializer
from services.api.serializer.unit import UnitSerializer
from services.tools.transaction import check_transaction


class ProductTransactionSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    unit = UnitSerializer()
    satisfied = serializers.SerializerMethodField()

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
        ]

    def get_satisfied(self, obj):
        return check_transaction(obj)
