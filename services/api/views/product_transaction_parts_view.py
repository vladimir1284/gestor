from inventory.models import ProductTransaction
from services.api.views.core.product_transaction_view import \
    ProductTransactionView


class ProductTransactionPartsView(ProductTransactionView):
    queryset = ProductTransaction.objects.filter(product__type="part").select_related(
        "unit",
        "product",
        "product__unit",
    )
