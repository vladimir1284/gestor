from inventory.models import Product
from services.api.views.core.products_view import ProductView


class ProductPartView(ProductView):
    queryset = Product.objects.filter(type="part", active=True).select_related("unit")
