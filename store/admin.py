from django.contrib import admin

from .models import (
    Associated,
    Product,
    Unit,
    Order,
    Transaction,
    StoreLocations,
    ProductCategory,
)


admin.site.register(Associated)
admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(Order)
admin.site.register(Transaction)
admin.site.register(StoreLocations)
admin.site.register(ProductCategory)
