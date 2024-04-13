from menu.menu.menu_element import MenuItem
from rbac.tools.permission_param import PermissionParam


MENU = [
    # Main menu
    MenuItem(
        name="Principal",
        i18n="Analytics",
        icon="bx-home-circle",
        url="dashboard",
        exact_match=True,
    ),
    MenuItem(
        name="Reportes",
        icon="bx-stats",
        children=[
            MenuItem(
                name="MANTENIMIENTO",
                i18n="Reportes",
                children=[
                    MenuItem(
                        name="Weekly",
                        url="weekly-report",
                        self_perm=PermissionParam(
                            code="services_report_weekly",
                            name="Reportes de mantenimiento por semana",
                        ),
                    ),
                    MenuItem(
                        name="Monthly",
                        url="monthly-report",
                        self_perm=PermissionParam(
                            code="services_report_monthly",
                            name="Reportes de mantenimiento por mes",
                        ),
                    ),
                ],
            ),
            MenuItem(
                name="RENTA",
                i18n="Reportes",
                children=[
                    MenuItem(
                        name="Monthly",
                        url="monthly-membership",
                        self_perm=PermissionParam(
                            code="rent_report_monthly",
                            name="Reportes de renta por mes",
                        ),
                    ),
                ],
            ),
        ],
    ),
    MenuItem(
        name="Asociados",
        icon="bx-user-circle",
        i18n="Negocio",
        children=[
            MenuItem(
                name="Clientes",
                url="list-client",
                self_perm=PermissionParam(
                    code="associated_clients",
                    name="Clientes asociados",
                ),
            ),
            MenuItem(
                name="Compañías",
                i18n="Companies",
                url="list-company",
                self_perm=PermissionParam(
                    code="associated_companies",
                    name="Compañías asociadas",
                ),
            ),
            MenuItem(
                name="Operarios",
                i18n="Usuarios",
                url="list-user",
                # dj_perms=["auth.add_user"],
                self_perm=PermissionParam(
                    code="associated_operators",
                    name="Operadores asociados",
                ),
                extra_match=[
                    "update-user",
                    "create-user",
                ],
            ),
            MenuItem(
                name="Users",
                url="rbac-list-users",
                # dj_perms=["auth.add_user"],
                extra_match=["rbac-role-form"],
                self_perm=PermissionParam(
                    code="user_admin",
                    name="Administrador de usuarios",
                ),
            ),
            MenuItem(
                name="Roles",
                url="rbac-list-roles",
                # dj_perms=["auth.add_user"],
                extra_match=["rbac-role-form"],
                self_perm=PermissionParam(
                    code="role_admin",
                    name="Administrador de roles",
                ),
            ),
        ],
    ),
    # Services menu
    MenuItem("MANTENIMIENTO"),
    MenuItem(
        name="Órdenes",
        i18n="Sells",
        icon="bx-wrench",
        url="list-service-order",
        self_perm=PermissionParam(
            code="service_order",
            name="Ordenes de servicio",
        ),
    ),
    MenuItem(
        name="Storage",
        icon="bxs-car-garage",
        url="storage-view",
        self_perm=PermissionParam(
            code="service_order_storage",
            name="Ordenes de servicio en storage",
        ),
    ),
    MenuItem(
        name="Taller",
        icon="bxs-car-mechanic",
        url="service-order-on-pos",
        self_perm=PermissionParam(
            code="service_order_on_pos",
            name="Ordenes de servicio en el taller",
        ),
    ),
    MenuItem(
        name="Configuración",
        i18n="Account Settings",
        icon="bx-cog",
        # dj_perms=["auth.add_user"],
        children=[
            MenuItem(
                name="Servicios",
                i18n="Usuarios",
                url="list-service",
                self_perm=PermissionParam(
                    code="service_services",
                    name="Servicios",
                ),
            ),
            MenuItem(
                name="Categorías",
                i18n="Clientes",
                url="list-service-category",
                self_perm=PermissionParam(
                    code="service_services_categories",
                    name="Categorías de servicios",
                ),
            ),
            MenuItem(
                name="Pagos",
                i18n="Payments",
                url="list-payment-category",
                self_perm=PermissionParam(
                    code="service_payment_categories",
                    name="Categorías de pagos",
                ),
            ),
        ],
    ),
    MenuItem(
        name="Gastos",
        i18n="Account Settings",
        icon="bx-credit-card",
        # dj_perms=["auth.add_user"],
        children=[
            MenuItem(
                name="Gastos",
                i18n="Sells",
                url="list-cost",
                self_perm=PermissionParam(
                    code="service_costs",
                    name="Costos de servicios",
                ),
            ),
            MenuItem(
                name="Categorías",
                i18n="Clientes",
                url="list-costs-category",
                self_perm=PermissionParam(
                    code="service_costs_categories",
                    name="Categorías de costos de servicios",
                ),
            ),
        ],
    ),
    # Rent menu
    MenuItem("RENTA"),
    MenuItem(
        name="Lessees",
        i18n="Sells",
        icon="bx-user",
        url="client-list",
        self_perm=PermissionParam(
            code="rent_clients",
            name="Clientes de renta",
        ),
    ),
    MenuItem(
        name="Trailers",
        i18n="Sells",
        icon="bx-traffic-cone",
        url="list-trailer",
        self_perm=PermissionParam(
            code="rent_trailers",
            name="Trailers de renta",
        ),
    ),
    MenuItem(
        name="Configuración",
        i18n="Account Settings",
        icon="bx-cog",
        # dj_perms=["auth.add_user"],
        children=[
            MenuItem(
                name="Tolls",
                icon="bx-traffic-cone",
                url="list-toll",
                self_perm=PermissionParam(
                    code="rent_toll",
                    name="Peajes de trailer de renta",
                ),
            ),
            MenuItem(
                name="Trackers",
                icon="bx-location-plus",
                url="trackers-table",
                self_perm=PermissionParam(
                    code="rent_tracker",
                    name="Rastreadores de trailer de renta",
                ),
            ),
            MenuItem(
                name="Gastos",
                i18n="Account Settings",
                icon="bx-credit-card",
                children=[
                    MenuItem(
                        name="Gastos",
                        i18n="Sells",
                        url="list-cost-rental",
                        self_perm=PermissionParam(
                            code="rent_cost",
                            name="Costos de renta",
                        ),
                    ),
                    MenuItem(
                        name="Categorías",
                        i18n="Clientes",
                        url="list-costs-rental-category",
                        self_perm=PermissionParam(
                            code="rent_cost_categories",
                            name="Categorías de costos de renta",
                        ),
                    ),
                ],
            ),
        ],
    ),
    # Inventary menu
    MenuItem(
        "INVENTARIO",
        # dj_perms=["auth.add_user"],
    ),
    MenuItem(
        name="Productos",
        i18n="Inventario",
        icon="bx-collection",
        url="list-product",
        # dj_perms=["auth.add_user"],
        self_perm=PermissionParam(
            code="inventory_products",
            name="Productos en el inventario",
        ),
    ),
    MenuItem(
        name="Configuración",
        i18n="Account Settings",
        icon="bx-cog",
        # dj_perms=["auth.add_user"],
        children=[
            MenuItem(
                name="Kits",
                i18n="Inventario",
                url="list-kit",
                self_perm=PermissionParam(
                    code="inventory_config_kits",
                    name="Configuración de kits en el inventario",
                ),
            ),
            MenuItem(
                name="Precios",
                url="minprice-product",
                self_perm=PermissionParam(
                    code="inventory_config_prices",
                    name="Configuración de precios en el inventario",
                ),
            ),
            MenuItem(
                name="Categorías",
                url="list-category",
                self_perm=PermissionParam(
                    code="inventory_config_categorías",
                    name="Configuración de categorías en el inventario",
                ),
            ),
            MenuItem(
                name="Unidades",
                url="list-unit",
                self_perm=PermissionParam(
                    code="inventory_config_units",
                    name="Configuración de unidades en el inventario",
                ),
            ),
        ],
    ),
    MenuItem(
        name="Compras",
        i18n="Account Settings",
        icon="bx-store",
        children=[
            MenuItem(
                name="Órdenes",
                i18n="Purchases",
                url="list-order",
                self_perm=PermissionParam(
                    code="inventory_buy_orders",
                    name="Ordenes de compra en el inventario",
                ),
            ),
            MenuItem(
                name="Proveedores",
                url="list-provider",
                self_perm=PermissionParam(
                    code="inventory_buy_providers",
                    name="Proveedores de compra en el inventario",
                ),
            ),
        ],
    ),
    # System Config
    MenuItem("System configuration"),
    MenuItem(
        "Templates",
        url="template-list",
        icon="bx-layout",
        extra_match=[
            "template-edit",
        ],
        self_perm=PermissionParam(
            code="system_conf_templates",
            name="Configuración de templates del sistema",
        ),
    ),
]


def getMenuCtx(request):
    return {"MenuItems": MENU}


def getMenuPermissions() -> list[PermissionParam]:
    perms = []
    for mi in MENU:
        perms += mi.get_permission_list()
    return perms
