from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from inventory.forms import KitTransactionCreateForm
from inventory.forms import TransactionCreateForm
from inventory.forms import TransactionProviderCreateForm
from inventory.models import convertUnit
from inventory.models import KitElement
from inventory.models import KitService
from inventory.models import Product
from inventory.models import ProductKit
from inventory.models import ProductTransaction
from inventory.models import Stock
from inventory.tools.transaction import renderCreateTransaction
from inventory.views.kit import computeKitData
from services.models import ServiceTransaction
from users.models import Associated
from utils.models import Order

# -------------------- Transaction ----------------------------


def getNewOrder(associated: Associated, product: Product, user):
    return Order.objects.create(
        concept="Restock of {}".format(product.name),
        note="Automatically created for the purchase of product {}. Please, check all details!".format(
            product.name
        ),
        type="purchase",
        associated=associated,
        created_by=user,
    )


@login_required
def create_kit_transaction(request, order_id, kit_id):
    order = get_object_or_404(Order, id=order_id)
    kit = get_object_or_404(ProductKit, id=kit_id)

    (elements, services, total, min_price) = computeKitData(kit)

    form = KitTransactionCreateForm(
        initial={"quantity": 1, "price": total, "tax": False}, min_price=min_price
    )

    if request.method == "POST":
        form = KitTransactionCreateForm(
            request.POST,
            initial={"quantity": 1, "price": total, "tax": False},
            min_price=min_price,
            kit=kit,
        )

        if form.is_valid():
            multiply = form.cleaned_data["quantity"]
            price = form.cleaned_data["price"]
            tax = form.cleaned_data["tax"]
            print(tax)

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
                        note=_(
                            f"Generated from kit {kit.name}.\nRemember to check the price and tax!"
                        ),
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
                        trans.quantity += multiply * convertUnit(
                            element.unit, trans.unit, element.quantity
                        )
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
                        note=_(
                            f"Generated from kit {kit.name}.\nRemember to check the price and tax!"
                        ),
                        price=element.product.getSuggestedPrice(),
                    )
                    if tax == False:
                        trans.tax = 0
                        trans.save()

            return redirect("detail-service-order", id=order_id)

    context = {
        "kit": kit,
        "elements": elements,
        "services": services,
        "total": total,
        "form": form,
    }
    return render(request, "inventory/kit_add.html", context)


@login_required
def create_transaction_new_order(request, product_id):
    product = Product.objects.get(id=product_id)
    initial = {"unit": product.unit}
    last_purchase = (
        ProductTransaction.objects.filter(order__type="purchase", product=product)
        .order_by("-id")
        .first()
    )
    order_id = -1
    if last_purchase:
        form = TransactionCreateForm(initial=initial, product=product)
    else:
        form = TransactionProviderCreateForm(initial=initial, product=product)
    if request.method == "POST":
        if last_purchase:
            last_provider = last_purchase.order.associated
        else:
            last_provider = Associated.objects.get(id=int(request.POST["associated"]))
        order = getNewOrder(last_provider, product, request.user)
        if last_purchase:
            form = TransactionCreateForm(request.POST, product=product, order=order)
        else:
            form = TransactionProviderCreateForm(
                request.POST, product=product, order=order
            )
        if form.is_valid():
            trans = form.save(commit=False)
            trans.order = order
            trans.product = product
            trans.save()
            return redirect("detail-order", id=order.id)
    context = renderCreateTransaction(request, form, product, order_id)
    return render(request, "inventory/transaction_create.html", context)


@login_required
def detail_transaction(request, id):
    # fetch the object related to passed id
    transaction = get_object_or_404(ProductTransaction, id=id)
    return render(
        request,
        "inventory/transaction_detail.html",
        {"transaction": transaction, "amount": getTransactionAmount(transaction)},
    )


def getTransactionAmount(transaction: ProductTransaction):
    return transaction.quantity * transaction.price * (1 + transaction.tax / 100.0)


def handle_transaction(transaction: ProductTransaction):
    #  To be performed on complete orders
    product = Product.objects.get(id=transaction.product.id)

    # To be used in the rest of the system
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity,
    )

    # TODO study taxes handling on sales to improve these formula
    # Generate stock
    cost = transaction.price * (1 + transaction.tax / 100.0)  # Add on taxes
    product.quantity += product_quantity
    product.stock_price += transaction.quantity * cost
    product.save()
    Stock.objects.create(
        product=product,
        quantity=product_quantity,
        cost=(transaction.quantity * cost) / product_quantity,
    )
