from inventory.models import convertUnit
from inventory.models import Product
from inventory.models import ProductTransaction
from inventory.models import ProductTransactionStock
from inventory.models import Stock
from inventory.tools.transaction import NotEnoughStockError
from inventory.views.product import discountStockFIFO
from utils.models import Order
from utils.models import Transaction


def reverse_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if (
        not isinstance(transaction, ProductTransaction)
        or not transaction.done
        or transaction.decline
    ):
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

    # Restore all stock
    stock_refs: list[ProductTransactionStock] = transaction.stock_refs.all()
    pending = product_quantity
    remainding_cost = stock_cost
    for sr in stock_refs:
        stock = sr.stock
        count = sr.quantity
        stock.quantity += count
        stock.save()
        pending -= count
        remainding_cost -= stock.cost
        sr.delete()

    # If there are parts with unreferenced stock create a new one
    if pending > 0:
        Stock.objects.create(
            product=product,
            quantity=pending,
            cost=remainding_cost / pending,
        )

    transaction.done = False
    transaction.save()


def reverse_order_transactions(order: Order):
    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        reverse_transaction(transaction)


def handle_transaction_stock(transaction: ProductTransaction):
    # Same as discountStockFIFO
    # But this will not remove the stocks
    # Will take the stock reference for transaction reversion
    product = transaction.product
    pending = convertUnit(
        input_unit=transaction.unit,
        output_unit=product.unit,
        value=transaction.quantity,
    )
    stock_cost = 0
    stock_array = Stock.objects.filter(
        product=product,
        quantity__gt=0,
    ).order_by("created_date")

    for stock in stock_array:
        if pending == 0:
            break

        count = max(min(pending, stock.quantity), 0)
        pending -= count

        stock.quantity -= count
        stock.save()

        ProductTransactionStock.objects.create(
            stock=stock,
            transaction=transaction,
            quantity=count,
        )

        stock_cost += count * stock.cost

    transaction.cost = stock_cost
    return stock_cost


def handle_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if (
        not isinstance(transaction, ProductTransaction)
        or transaction.done
        or transaction.decline
    ):
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

    # stock_cost = discountStockFIFO(product, product_quantity)
    stock_cost = handle_transaction_stock(transaction)
    transaction.done = True
    transaction.save()

    product.quantity -= product_quantity
    product.stock_price -= stock_cost
    product.save()


def handle_order_transactions(order: Order, decline_unsatisfied: bool = False):
    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        if decline_unsatisfied and not check_transaction(transaction):
            decline_transaction(transaction)
        else:
            handle_transaction(transaction)


def decline_transaction(transaction: Transaction):
    if not isinstance(transaction, ProductTransaction) or transaction.decline:
        return None

    if transaction.done:
        reverse_transaction(transaction)

    transaction.decline = True
    transaction.save()


def decline_order_transaction(
    order: Order,
    done: bool = False,
    satisfied: bool = False,
):
    transactions = ProductTransaction.objects.filter(order=order)
    for transaction in transactions:
        if not done and transaction.done:
            continue
        if not satisfied and check_transaction(transaction):
            continue
        decline_transaction(transaction)


def check_transaction(transaction: Transaction) -> bool | None:
    if not isinstance(transaction, ProductTransaction) or transaction.decline:
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
