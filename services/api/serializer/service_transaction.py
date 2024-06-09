from django.shortcuts import get_object_or_404
from rest_framework import serializers

from services.api.serializer.service import ServiceSerializer
from services.models import Service
from services.models import ServiceTransaction


class ServiceTransactionSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField()

    class Meta:
        model = ServiceTransaction
        fields = [
            "id",
            "service",
            "tax",
            "price",
            "quantity",
            "service_id",
        ]
        read_only_fields = [
            "id",
            "service",
        ]

    def create(self, validated_data: dict):
        service_id = validated_data.get("service_id")
        service: Service = get_object_or_404(Service, id=service_id)

        validated_data["service"] = service

        return super().create(validated_data)
