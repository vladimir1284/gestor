from django.utils.translation import gettext_lazy as _

from inventory.models import PriceReference
from inventory.models import Product
from inventory.models import Unit


class NotEnoughStockError(BaseException):
    """
    Raised when the input and output units
    doesn't measure the same magnitude
    """


def renderCreateTransaction(request, form, product: Product, order_id):
    price_references = PriceReference.objects.filter(product=product)
    units = [product.unit]
    units_qs = Unit.objects.filter(magnitude=product.unit.magnitude).exclude(
        id=product.unit.id
    )
    for unit in units_qs:
        units.append(unit)
    title = _("Create Transaction")
    if product.type == "part":
        title = _("Add part")
    if product.type == "consumable":
        title = _("Add consumable")
    context = {
        "form": form,
        "product": product,
        "suggested": product.getSuggestedPrice(),
        "cost": product.getCost(),
        "order_id": order_id,
        "price_references": price_references,
        "title": title,
        "units": units,
        "create": True,
    }
    return context
