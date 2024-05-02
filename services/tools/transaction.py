from inventory.models import convertUnit
from inventory.models import Product
from inventory.models import ProductTransaction
from inventory.models import Stock
from inventory.tools.transaction import NotEnoughStockError
from inventory.views.product import discountStockFIFO
from utils.models import Order
from utils.models import Transaction


def reverse_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if not isinstance(transaction, ProductTransaction):
        return
    if not transaction.done:
        return

    product = transaction.product
    # To be used in the rest of the system
    # product = Product.objects.get(id=product.id)
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity,
    )

    stock_cost = transaction.cost

    product.quantity += product_quantity
    product.stock_price += stock_cost
    product.save()

    Stock.objects.create(
        product=product,
        quantity=product_quantity,
        cost=stock_cost / product_quantity,
    )

    transaction.done = False
    transaction.save()


def reverse_order_transactions(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        reverse_transaction(transaction)


def handle_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if not isinstance(transaction, ProductTransaction):
        return
    if transaction.done:
        return

    product = transaction.product
    # To be used in the rest of the system
    product = Product.objects.get(id=product.id)
    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity,
    )

    if product_quantity > product.quantity:
        raise NotEnoughStockError

    stock_cost = discountStockFIFO(product, product_quantity)
    transaction.cost = stock_cost
    transaction.done = True
    transaction.save()

    product.quantity -= product_quantity
    product.stock_price -= stock_cost
    product.save()


def handle_order_transactions(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        handle_transaction(transaction)


def check_transaction(transaction: Transaction) -> bool | None:
    if not isinstance(transaction, ProductTransaction):
        return None

    if transaction.done:
        return True

    product: Product = transaction.product

    product_quantity = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity,
    )

    if product_quantity > product.quantity:
        return False

    return True


def check_order_transactions(order: Order, set: bool = True) -> bool | None:
    all_satisfied = True

    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        satisfied = check_transaction(transaction)
        if satisfied is None:
            continue
        if set:
            transaction.satisfied = satisfied
        if not satisfied:
            all_satisfied = False

    if set:
        order.satisfied = all_satisfied

    return all_satisfied
