from menu.menu.menu import PermissionParam


EXTRA_PERMS = [
    PermissionParam(
        code="export_clients",
        app="extra_perm",
        name="Can export clients",
    ),
    PermissionParam(
        code="disabled_products",
        app="extra_perm",
        name="Productos desavilitados en el inventario",
    ),
    PermissionParam(
        code="order_discount",
        app="extra_perm",
        name="Descuentos en ordenes",
    ),
    PermissionParam(
        code="inventary_product_cost",
        app="extra_perm",
        name="Costos de productos en inventario",
    ),
]
