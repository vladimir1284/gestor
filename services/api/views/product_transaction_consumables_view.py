from inventory.models import ProductTransaction
from services.api.views.core.product_transaction_view import \
    ProductTransactionView


class ProductTransactionConsumablesView(ProductTransactionView):
    queryset = ProductTransaction.objects.filter(
        product__type="consumable"
    ).select_related(
        "unit",
        "product",
        "product__unit",
    )
