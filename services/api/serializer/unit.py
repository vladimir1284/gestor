from rest_framework import serializers

from inventory.models import Unit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
            "factor",
            "magnitude",
        ]
