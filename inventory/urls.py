from django.urls import path
from .views import (
    category, kit, order, product, transaction, unit
)


urlpatterns = [
    # -------------------- Category ----------------------------
    path('create-category/', category.CategoryCreateView.as_view(),
         name='create-category'),
    path('update-category/<pk>', category.CategoryUpdateView.as_view(),
         name='update-category'),
    path('list-category/', category.CategoryListView.as_view(), name='list-category'),
    path('delete-category/<id>', category.delete_category, name='delete-category'),
    # -------------------- Order ----------------------------
    path('select-provider/', order.select_provider, name='select-provider'),
    path('create-order/', order.create_order, name='create-order'),
    path('create-order/<product_id>', order.create_order,
         name='create-order-from-product'),
    path('update-order/<id>', order.update_order, name='update-order'),
    path('detail-order/<id>', order.detail_order, name='detail-order'),
    path('list-order/', order.list_order, name='list-order'),
    path('list-terminated-order/', order.list_terminated_order,
         name='list-order-terminated'),
    path('update-order-status/<id>/<status>',
         order.update_order_status, name='update-order-status'),
    # -------------------- Transaction ----------------------------
    path('create-transaction/<order_id>/<product_id>',
         transaction.create_transaction, name='create-transaction'),
    path('create-transaction-new-order/<product_id>',
         transaction.create_transaction_new_order, name='create-transaction-new-order'),
    path('update-transaction/<id>', transaction.update_transaction,
         name='update-transaction'),
    path('detail-transaction/<id>', transaction.detail_transaction,
         name='detail-transaction'),
    path('delete-transaction/<id>', transaction.delete_transaction,
         name='delete-transaction'),
    # -------------------- Unit ----------------------------
    path('create-unit/', unit.create_unit, name='create-unit'),
    path('update-unit/<id>', unit.update_unit, name='update-unit'),
    path('list-unit/', unit.list_unit, name='list-unit'),
    path('delete-unit/<id>', unit.delete_unit, name='delete-unit'),
    # -------------------- Product ----------------------------
    path('export-inventory/', product.export_inventory, name='export-inventory'),
    path('create-product/', product.create_product, name='create-product'),
    path('update-product/<id>', product.update_product, name='update-product'),
    path('detail-product/<id>', product.detail_product, name='detail-product'),
    path('duplicate-product/<id>', product.duplicate_product,
         name='duplicate-product'),
    path('list-product/', product.list_product, name='list-product'),
    path('deactivated_product_list/', product.list_deactivated_product,
         name='deactivated-product-list'),
    path('minprice-product/', product.minprice_product, name='minprice-product'),
    path('minprice-update/', product.minprice_update, name='minprice-update'),
    path('quantity-update/', product.quantity_update, name='quantity-update'),
    path('select-product/<next>/<order_id>',
         product.select_product, name='select-product'),
    path('select-new-product/<next>/<order_id>',
         product.select_new_product, name='select-new-product'),
    path('delete-product/<id>', product.delete_product, name='delete-product'),
    # -------------------- Price Reference ---------------------
    path('create-price/<product_id>', product.create_price, name='create-price'),
    path('update-price/<id>', product.update_price, name='update-price'),
    path('delete-price/<id>', product.delete_price, name='delete-price'),
    # ------------------------- Kits ----------------------------
    path('list-kit/', kit.list_kit, name='list-kit'),
    path('detail-kit/<id>', kit.detail_kit, name='detail-kit'),
    path('create-kit/', kit.create_kit, name='create-kit'),
    path('update-kit/<id>', kit.update_kit, name='update-kit'),
    path('delete-kit/<id>', kit.delete_kit, name='delete-kit'),
    path('select_kit_product/<kit_id>',
         kit.select_kit_product, name='add-kit-product'),
    # --------------------- Kit Elements ------------------------
    path('create-kit-element/<kit_id>/<product_id>',
         kit.create_kit_element, name='create-kit-element'),
    path('delete-kit-element/<id>', kit.delete_kit_element,
         name='delete-kit-element'),
    path('update-kit-element/<id>', kit.update_kit_element,
         name='update-kit-element'),
    path('create-kit-transaction/<order_id>/<kit_id>',
         transaction.create_kit_transaction, name='create-kit-transaction'),
    # --------------------- Kit Services ------------------------
    path('create-kit-service/<kit_id>/<service_id>',
         kit.create_kit_service, name='create-kit-service'),
    path('delete-kit-service/<id>', kit.delete_kit_service,
         name='delete-kit-service'),
]
