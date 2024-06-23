from rest_framework import serializers

from inventory.models import ProductKit
from services.api.serializer.kit_element import KitElementSerializer
from services.api.serializer.kit_service import KitServiceSerializer
from services.tools.transaction import convertUnit


class ProductKitSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    suggested_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductKit
        fields = [
            "id",
            "name",
            "available",
            "elements",
            "services",
            "min_price",
            "suggested_price",
        ]

    def get_available(self, kit: ProductKit):
        elements = kit.kitelement_set.all()
        for element in elements:
            element.product.available = convertUnit(
                element.product.unit,
                element.unit,
                element.product.computeAvailable(),
            )
            if element.product.available < element.quantity:
                return False

        return True

    def get_elements(self, kit: ProductKit):
        elements = kit.kitelement_set.all()
        serializer = KitElementSerializer(elements, many=True)
        return serializer.data

    def get_services(self, kit: ProductKit):
        services = kit.kitservice_set.all()
        serializer = KitServiceSerializer(services, many=True)
        return serializer.data

    def get_min_price(self, kit: ProductKit):
        min_price = 0
        elements = kit.kitelement_set.all()
        for element in elements:
            min_price += element.quantity * convertUnit(
                element.product.unit,
                element.unit,
                element.product.min_price,
            )
        return min_price

    def get_suggested_price(self, kit: ProductKit):
        suggested_price = 0

        elements = kit.kitelement_set.all()
        for element in elements:
            suggested_price += element.quantity * convertUnit(
                element.product.unit,
                element.unit,
                element.product.getSuggestedPrice(),
            )

        services = kit.kitservice_set.all()
        for service in services:
            suggested_price += service.service.suggested_price

        return suggested_price


class ProductKitCreationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    price = serializers.FloatField()
    tax = serializers.BooleanField()
