from rest_framework import routers

from services.api.views.kits_view import KitView
from services.api.views.product_consumables_view import ProductConsumableView
from services.api.views.product_parts_view import ProductPartView
from services.api.views.product_transaction_consumables_view import \
    ProductTransactionConsumablesView
from services.api.views.product_transaction_parts_view import \
    ProductTransactionPartsView
from services.api.views.service_transaction_view import ServiceTransactionView
from services.api.views.service_view import ServiceView

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
# Apis for order services
router.register(
    r"services",
    ServiceView,
    basename="services",
)
router.register(
    r"services_transaction/(?P<order_id>\d+)",
    ServiceTransactionView,
    basename="services-transaction",
)
# Apis for kits
router.register(
    r"kits/(?P<order_id>\d+)",
    KitView,
    basename="kits",
)

urlpatterns = router.urls
