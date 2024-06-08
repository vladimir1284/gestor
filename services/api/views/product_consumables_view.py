from inventory.models import Product
from services.api.views.core.products_view import ProductView


class ProductConsumableView(ProductView):
    queryset = Product.objects.filter(type="consumable", active=True)
