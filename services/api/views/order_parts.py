from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import ProductTransaction
from services.api.serializer.product_transaction import \
    ProductTransactionSerializer
from utils.models import Order


class OrderPartsViewSet(APIView):
    def get(self, request: HttpRequest, order_id: int):
        order: Order = get_object_or_404(Order, id=order_id)

        parts = ProductTransaction.objects.filter(order=order)
        serParts = ProductTransactionSerializer(parts, many=True)
        data = serParts.data

        return Response(data)
