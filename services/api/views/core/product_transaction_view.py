from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from inventory.models import ProductTransaction
from services.api.serializer.product_transaction import \
    ProductTransactionSerializer
from services.tools.transaction import check_transaction
from services.tools.transaction import handle_transaction
from services.tools.transaction import reverse_transaction
from utils.models import Order


class ProductTransactionView(viewsets.ModelViewSet):
    serializer_class = ProductTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(order__id=self.kwargs["order_id"])

    @atomic
    def create(self, request: Request, order_id: int):
        serializer = ProductTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order: Order = get_object_or_404(Order, id=order_id)
        part: ProductTransaction = serializer.save(order=order)

        if (
            order.type == "sell"
            and order.status != "pending"
            and order.status != "decline"
            and check_transaction(part)
        ):
            handle_transaction(part)

        return Response({})

    @atomic
    def update(self, request: Request, order_id: int, pk: int):
        before: ProductTransaction = self.get_object()
        serializer = ProductTransactionSerializer(instance=before, data=request.data)
        serializer.is_valid(raise_exception=True)

        order: Order = get_object_or_404(Order, id=order_id)

        if (
            order.type == "sell"
            and order.status != "pending"
            and order.status != "decline"
        ):
            reverse_transaction(before)

        part: ProductTransaction = serializer.save(order=order)
        if (
            order.type == "sell"
            and order.status != "pending"
            and order.status != "decline"
            and check_transaction(part)
        ):
            handle_transaction(part)

        return Response({})

    @atomic
    def destroy(self, request, *args, **kwargs):
        print(args, kwargs)

        transaction: ProductTransaction = self.get_object()

        if (
            transaction.order.type == "sell"
            and transaction.order.status != "pending"
            and transaction.order.status != "decline"
        ):
            reverse_transaction(transaction)

        return super().destroy(request, *args, **kwargs)
