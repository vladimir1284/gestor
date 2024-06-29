from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from inventory.models import KitElement
from inventory.models import KitService
from inventory.models import Product
from inventory.models import ProductKit
from inventory.models import ProductTransaction
from inventory.views.kit import computeKitData
from services.api.serializer.product_kit import ProductKitCreationSerializer
from services.api.serializer.product_kit import ProductKitSerializer
from services.models import Service
from services.models import ServiceTransaction
from services.tools.transaction import check_transaction
from services.tools.transaction import convertUnit
from services.tools.transaction import handle_transaction
from services.tools.transaction import reverse_transaction
from utils.models import Order


def findTrnasByProduct(
    prod_trans: list[ProductTransaction], id: int
) -> ProductTransaction | None:
    for trans in prod_trans:
        if trans.product.id == id:
            return trans
    return None


def findTrnasByService(
    serv_trans: list[ServiceTransaction], id: int
) -> ServiceTransaction | None:
    for trans in serv_trans:
        if trans.service.id == id:
            return trans
    return None


class KitTransactionView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request: Request, order_id: int):
        kits = (
            ProductKit.objects.all()
            .order_by("name")
            .prefetch_related(
                "kitservice_set",
                "kitservice_set__service",
                "kitelement_set",
                "kitelement_set__unit",
                "kitelement_set__product",
                "kitelement_set__product__unit",
            )
        )
        serializer = ProductKitSerializer(kits, many=True)
        return Response(serializer.data)

    @atomic
    def create(self, request: Request, order_id: int):
        kit_name = request.data["name"]

        order: Order = get_object_or_404(Order, id=order_id)

        prod_trans: list[ProductTransaction] = order.producttransaction_set.all()
        serv_trans: list[ServiceTransaction] = order.servicetransaction_set.all()

        products_id = [element["product"]["id"] for element in request.data["elements"]]
        services_id = [service["service"]["id"] for service in request.data["services"]]

        products = Product.objects.filter(id__in=products_id)
        services = Service.objects.filter(id__in=services_id)

        products_map = {}
        for p in products:
            products_map[p.id] = p

        services_map = {}
        for s in services:
            services_map[s.id] = s

        for element in request.data["elements"]:
            product_id = element["product"]["id"]
            qty = element["new_quantity"]
            price = element["new_price"]
            tax = element["new_tax"]

            trans = findTrnasByProduct(prod_trans, product_id)
            if trans is not None:
                if (
                    order.type == "sell"
                    and order.status != "pending"
                    and order.status != "decline"
                ):
                    reverse_transaction(trans)

                trans.quantity += qty
                # trans.tax = tax

                if (
                    order.type == "sell"
                    and order.status != "pending"
                    and order.status != "decline"
                    and check_transaction(trans)
                ):
                    handle_transaction(trans)
            else:
                if product_id not in products_map:
                    continue
                prod = products_map[product_id]
                trans = ProductTransaction.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit=prod.unit,
                    note=f"Generated from kit {kit_name}.\nRemember to check the price and tax!",
                    price=price,
                    active_tax=tax,
                )
                if (
                    order.type == "sell"
                    and order.status != "pending"
                    and order.status != "decline"
                    and check_transaction(trans)
                ):
                    handle_transaction(trans)

        for service in request.data["services"]:
            service_id = service["service"]["id"]
            price = service["new_price"]

            trans = findTrnasByService(serv_trans, service_id)
            if trans is None:
                if service_id not in services_map:
                    continue
                serv = services_map[service_id]
                trans = ServiceTransaction.objects.create(
                    order=order,
                    service=serv,
                    quantity=1,
                    note=f"Generated from kit {kit_name}.\nRemember to check the price!",
                    price=price,
                )

        # serializer = ProductKitSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data

        # kit: ProductKit = get_object_or_404(ProductKit, id=data["id"])
        #
        # (elements, services, total, min_price) = computeKitData(kit)
        #
        # multiply = data["quantity"]
        # price = data["price"]
        # tax = data["tax"]
        #
        # # Handle price change
        # load2service = 0
        # if price != total:
        #     diff = price - total
        #     if diff < 0:  # Discount
        #         order.discount = -multiply * diff
        #         order.save()
        #     else:  # Profit
        #         load2service = multiply * diff
        #
        # # Add services
        # kitServices = KitService.objects.filter(kit=kit)
        # transactions = ServiceTransaction.objects.filter(order=order)
        # for service in kitServices:
        #     inOrder = False
        #     # Check for products in the order
        #     for trans in transactions:
        #         if service.service == trans.service:
        #             # Add to a product present in the order
        #             trans.quantity += multiply
        #             trans.price += load2service / trans.quantity
        #             trans.save()
        #             inOrder = True
        #             break
        #     if not inOrder:
        #         # New product transaction
        #         if load2service > 0:
        #             service.service.suggested_price += load2service / multiply
        #         trans = ServiceTransaction.objects.create(
        #             order=order,
        #             service=service.service,
        #             quantity=multiply,
        #             note=f"Generated from kit {kit.name}.\nRemember to check the price and tax!",
        #             price=service.service.suggested_price,
        #         )
        #         if tax == False:
        #             trans.tax = 0
        #             trans.save()
        #     load2service = 0
        #
        # # Add products
        # elements = KitElement.objects.filter(kit=kit)
        # transactions = ProductTransaction.objects.filter(order=order)
        # for element in elements:
        #     inOrder = False
        #     # Check for products in the order
        #     for trans in transactions:
        #         if element.product == trans.product:
        #             # Add to a product present in the order
        #             if (
        #                 order.type == "sell"
        #                 and order.status != "pending"
        #                 and order.status != "decline"
        #             ):
        #                 reverse_transaction(trans)
        #
        #             trans.quantity += multiply * convertUnit(
        #                 element.unit, trans.unit, element.quantity
        #             )
        #
        #             if (
        #                 order.type == "sell"
        #                 and order.status != "pending"
        #                 and order.status != "decline"
        #                 and check_transaction(trans)
        #             ):
        #                 handle_transaction(trans)
        #
        #             trans.save()
        #             inOrder = True
        #             break
        #
        #     if not inOrder:
        #         # New product transaction
        #         trans = ProductTransaction.objects.create(
        #             order=order,
        #             product=element.product,
        #             quantity=element.quantity * multiply,
        #             unit=element.unit,
        #             note=f"Generated from kit {kit.name}.\nRemember to check the price and tax!",
        #             price=element.product.getSuggestedPrice(),
        #         )
        #         if (
        #             order.type == "sell"
        #             and order.status != "pending"
        #             and order.status != "decline"
        #             and check_transaction(trans)
        #         ):
        #             handle_transaction(trans)
        #
        #         if tax == False:
        #             trans.tax = 0
        #
        #         trans.save()

        return Response(status=200)
