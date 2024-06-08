from rest_framework import routers

from services.api.views.product_consumables_view import ProductConsumableView
from services.api.views.product_parts_view import ProductPartView
from services.api.views.product_transaction_consumables_view import \
    ProductTransactionConsumablesView
from services.api.views.product_transaction_parts_view import \
    ProductTransactionPartsView

router = routers.SimpleRouter()
# Apis for order parts
router.register(
    r"product/parts",
    ProductPartView,
    basename="product-parts",
)
router.register(
    r"product_transaction/parts/(?P<order_id>\d+)",
    ProductTransactionPartsView,
    basename="product-transaction-parts",
)
# Apis for order consumables
router.register(
    r"product/consumables",
    ProductConsumableView,
    basename="product-consumables",
)
router.register(
    r"product_transaction/consumables/(?P<order_id>\d+)",
    ProductTransactionConsumablesView,
    basename="product-transaction-consumables",
)

urlpatterns = router.urls
