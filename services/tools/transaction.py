from inventory.models import (
    convertUnit,
)
from inventory.models import Product
from inventory.models import ProductTransaction
from inventory.views.product import discountStockFIFO
from inventory.views.transaction import (
    NotEnoughStockError,
)
from utils.models import (
    Transaction,
)


def handle_transaction(transaction: Transaction):
    #  To be performed on complete orders
    if isinstance(transaction, ProductTransaction):
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
        transaction.save()

        product.quantity -= product_quantity
        product.stock_price -= stock_cost
        product.save()
