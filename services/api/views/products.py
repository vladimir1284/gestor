from rest_framework import permissions
from rest_framework import viewsets

from inventory.models import Product
from services.api.serializer.product import ProductSerializer


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.filter(type="part", active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ["GET"]
