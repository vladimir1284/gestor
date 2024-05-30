from django.urls import path

from services.api.views.order_parts import OrderPartsViewSet

urlpatterns = [
    path("order_parts/<order_id>", OrderPartsViewSet.as_view()),
]
