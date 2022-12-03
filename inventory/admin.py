from django.contrib import admin

from .models import (
    Product,
    Stock,
    Profit,
    Unit,
    Transaction,
    InventoryLocations,
    ProductCategory,
)


admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(Transaction)
admin.site.register(InventoryLocations)
admin.site.register(ProductCategory)
admin.site.register(Stock)
admin.site.register(Profit)
