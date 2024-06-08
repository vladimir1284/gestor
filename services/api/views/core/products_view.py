from rest_framework import permissions
from rest_framework import viewsets

from services.api.serializer.product import ProductSerializer


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ["GET"]
