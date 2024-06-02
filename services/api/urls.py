from rest_framework import routers

from services.api.views.order_parts import OrderPartsView
from services.api.views.products import ProductView

router = routers.SimpleRouter()
router.register(r"products", ProductView)
router.register(r"order_parts/(?P<order_id>\d+)", OrderPartsView)

urlpatterns = router.urls
