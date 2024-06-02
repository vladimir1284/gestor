from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from inventory.models import Product
from inventory.models import ProductTransaction
from services.api.serializer.product import ProductSerializer
from services.api.serializer.unit import UnitSerializer
from services.tools.transaction import check_transaction
from services.tools.transaction import handle_transaction


class ProductTransactionSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    satisfied = serializers.SerializerMethodField(read_only=True)
    product_id = serializers.IntegerField()

    class Meta:
        model = ProductTransaction
        fields = [
            # read_only
            "id",
            "product",
            "unit",
            "cost",
            "done",
            "decline",
            "satisfied",
            # read_write
            "product_id",
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
        ]

    def get_satisfied(self, trans: ProductTransaction):
        return check_transaction(trans)

    def create(self, validated_data: dict):
        product_id = validated_data.get("product_id")
        product: Product = get_object_or_404(Product, id=product_id)

        validated_data["product"] = product
        validated_data["unit"] = product.unit

        return super().create(validated_data)
