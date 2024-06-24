from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from services.api.serializer.service_transaction import \
    ServiceTransactionSerializer
from services.models import ServiceTransaction
from utils.models import Order


class ServiceTransactionView(viewsets.ModelViewSet):
    queryset = ServiceTransaction.objects.all().select_related("service")
    serializer_class = ServiceTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__id=self.kwargs["order_id"])

    @atomic
    def create(self, request: Request, order_id: int):
        serializer = ServiceTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order: Order = get_object_or_404(Order, id=order_id)
        serializer.save(order=order)

        return Response({})
