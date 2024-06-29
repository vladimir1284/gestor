from django.db.transaction import atomic
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from inventory.models import ProductKit
from services.api.serializer.product_kit import KitElementSerializer
from services.api.serializer.product_kit import KitServiceSerializer
from services.api.serializer.product_kit import ProductKitSerializer


class KitView(viewsets.ModelViewSet):
    queryset = ProductKit.objects.all().prefetch_related(
        "kitservice_set",
        "kitservice_set__service",
        "kitelement_set",
        "kitelement_set__unit",
        "kitelement_set__product",
        "kitelement_set__product__unit",
    )
    serializer_class = ProductKitSerializer
    permission_classes = [permissions.IsAuthenticated]

    @atomic
    def create(self, request: Request):
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        kit = serializer.save()

        for element in data["services"]:
            element["kit"] = kit.id
            service_id = element["service"]["id"]
            es = KitServiceSerializer(data=element)
            es.is_valid(raise_exception=True)
            es.save(service_id=service_id)

        for element in data["elements"]:
            element["kit"] = kit.id
            product_id = element["product"]["id"]
            unit_id = element["product"]["unit"]["id"]
            es = KitElementSerializer(data=element)
            es.is_valid(raise_exception=True)
            es.save(
                product_id=product_id,
                unit_id=unit_id,
            )

        return Response(status=201)
