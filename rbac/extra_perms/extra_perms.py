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
        code="rental_debts_total",
        app="extra_perm",
        name="Mostrar el valor total de la deuda de alquiler",
    ),
    PermissionParam(
        code="inventary_product_cost",
        app="extra_perm",
        name="Costos de productos en inventario",
    ),
    PermissionParam(
        code="costs_access",
        app="extra_perm",
        name="Acceso a costos",
    ),
    PermissionParam(
        code="costs_edit",
        app="extra_perm",
        name="Modificación de costos",
    ),
]
