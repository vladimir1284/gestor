from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from inventory.models import KitElement
from inventory.models import KitService
from inventory.models import ProductKit
from inventory.models import ProductTransaction
from inventory.views.kit import computeKitData
from services.api.serializer.product_kit import ProductKitCreationSerializer
from services.api.serializer.product_kit import ProductKitSerializer
from services.models import ServiceTransaction
from services.tools.transaction import check_transaction
from services.tools.transaction import convertUnit
from services.tools.transaction import handle_transaction
from services.tools.transaction import reverse_transaction
from utils.models import Order


class KitView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request: Request, order_id: int):
        kits = ProductKit.objects.all().order_by("name")
        serializer = ProductKitSerializer(kits, many=True)
        return Response(serializer.data)

    @atomic
    def create(self, request: Request, order_id: int):
        order: Order = get_object_or_404(Order, id=order_id)

        serializer = ProductKitCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        kit: ProductKit = get_object_or_404(ProductKit, id=data["id"])

        (elements, services, total, min_price) = computeKitData(kit)

        multiply = data["quantity"]
        price = data["price"]
        tax = data["tax"]

        # Handle price change
        load2service = 0
        if price != total:
            diff = price - total
            if diff < 0:  # Discount
                order.discount = -multiply * diff
                order.save()
            else:  # Profit
                load2service = multiply * diff

        # Add services
        kitServices = KitService.objects.filter(kit=kit)
        transactions = ServiceTransaction.objects.filter(order=order)
        for service in kitServices:
            inOrder = False
            # Check for products in the order
            for trans in transactions:
                if service.service == trans.service:
                    # Add to a product present in the order
                    trans.quantity += multiply
                    trans.price += load2service / trans.quantity
                    trans.save()
                    inOrder = True
                    break
            if not inOrder:
                # New product transaction
                if load2service > 0:
                    service.service.suggested_price += load2service / multiply
                trans = ServiceTransaction.objects.create(
                    order=order,
                    service=service.service,
                    quantity=multiply,
                    note=f"Generated from kit {kit.name}.\nRemember to check the price and tax!",
                    price=service.service.suggested_price,
                )
                if tax == False:
                    trans.tax = 0
                    trans.save()
            load2service = 0

        # Add products
        elements = KitElement.objects.filter(kit=kit)
        transactions = ProductTransaction.objects.filter(order=order)
        for element in elements:
            inOrder = False
            # Check for products in the order
            for trans in transactions:
                if element.product == trans.product:
                    # Add to a product present in the order
                    if (
                        order.type == "sell"
                        and order.status != "pending"
                        and order.status != "decline"
                    ):
                        reverse_transaction(trans)

                    trans.quantity += multiply * convertUnit(
                        element.unit, trans.unit, element.quantity
                    )

                    if (
                        order.type == "sell"
                        and order.status != "pending"
                        and order.status != "decline"
                        and check_transaction(trans)
                    ):
                        handle_transaction(trans)

                    trans.save()
                    inOrder = True
                    break

            if not inOrder:
                # New product transaction
                trans = ProductTransaction.objects.create(
                    order=order,
                    product=element.product,
                    quantity=element.quantity * multiply,
                    unit=element.unit,
                    note=f"Generated from kit {kit.name}.\nRemember to check the price and tax!",
                    price=element.product.getSuggestedPrice(),
                )
                if (
                    order.type == "sell"
                    and order.status != "pending"
                    and order.status != "decline"
                    and check_transaction(trans)
                ):
                    handle_transaction(trans)

                if tax == False:
                    trans.tax = 0

                trans.save()

        return Response(status=200)
