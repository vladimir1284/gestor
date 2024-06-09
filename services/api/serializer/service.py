from rest_framework import serializers

from services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "created_date",
            # "category",
            "sell_tax",
            "suggested_price",
            # Special services
            "tire",
            # Services that doesn't appear in the invoice
            "internal",
            # Actions related to marketing tha should be carried out by the employee
            "marketing",
        ]
