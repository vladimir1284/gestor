from django.contrib import admin

from .models import (
    Associated,
    Product,
    Stock,
    Profit,
    Unit,
    Order,
    Transaction,
    InventoryLocations,
    ProductCategory,
)


admin.site.register(Associated)
admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(Order)
admin.site.register(Transaction)
admin.site.register(InventoryLocations)
admin.site.register(ProductCategory)
admin.site.register(Stock)
admin.site.register(Profit)