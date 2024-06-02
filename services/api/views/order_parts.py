from django.db.transaction import atomic
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import ProductTransaction
from services.api.serializer.product_transaction import \
    ProductTransactionSerializer
from services.tools.transaction import reverse_transaction
from utils.models import Order


class OrderPartsView(viewsets.ModelViewSet):
    queryset = ProductTransaction.objects.filter(product__type="part")
    serializer_class = ProductTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__id=self.kwargs["order_id"])

    @atomic
    def destroy(self, request, *args, **kwargs):
        print(args, kwargs)

        transaction: ProductTransaction = self.get_object()

        if transaction.order.type == "sell":
            if (
                transaction.order.status != "pending"
                and transaction.order.status != "decline"
            ):
                reverse_transaction(transaction)

        return super().destroy(request, *args, **kwargs)
