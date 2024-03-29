from django.contrib import admin

from .models import (
    Product,
    Stock,
    Unit,
    ProductTransaction,
    InventoryLocations,
    ProductCategory,
    PriceReference,
    ProductKit,
    KitElement
)


admin.site.register(Product)
admin.site.register(Unit)
admin.site.register(ProductTransaction)
admin.site.register(InventoryLocations)
admin.site.register(ProductCategory)
admin.site.register(Stock)
admin.site.register(PriceReference)
admin.site.register(ProductKit)
admin.site.register(KitElement)
