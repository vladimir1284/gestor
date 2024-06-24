from rest_framework import serializers

from services.models import Service
from services.models import ServiceTransaction


class ServiceSerializer(serializers.ModelSerializer):
    sells_num = serializers.SerializerMethodField()
    total_sells = serializers.SerializerMethodField()

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
            # Statistics
            "sells_num",
            "total_sells",
        ]

    def get_sells_num(self, serv: Service):
        trans: list[ServiceTransaction] = serv.servicetransaction_set.all()
        return len(trans)

    def get_total_sells(self, serv: Service):
        trans: list[ServiceTransaction] = serv.servicetransaction_set.all()
        sells_count = [t.quantity for t in trans]
        total = float(sum(sells_count))
        return total
