from django.db import models

from equipment.models import Vehicle
from rent.models.vehicle import Trailer
from services.models.preorder_data import PreorderData
from users.models import Company
from utils.models import Order


MAINTENANCE = "Maintenance to trailer"
QUOTATION = "Quotation"
PARTS_SALE = "Parts' sale"

ORDER_CONCEPT = [
    MAINTENANCE,
    QUOTATION,
    PARTS_SALE,
]


class Preorder(models.Model):
    preorder_data = models.ForeignKey(
        PreorderData,
        on_delete=models.SET_NULL,
        null=True,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
    )
    trailer = models.ForeignKey(
        Trailer,
        on_delete=models.SET_NULL,
        null=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
    )
    equipment_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=Order.EQUIPMENT_TYPE_CHOICE,
    )
    concept = models.CharField(
        max_length=120,
        default=MAINTENANCE,
        choices=ORDER_CONCEPT,
    )
    creating_order = models.BooleanField(default=True)
    using_signature = models.BooleanField(default=False)
    completed = models.BooleanField(null=True)

    @property
    def external(self):
        return (
            self.trailer is None
            and self.vehicle is None
            and self.company is None
            and self.preorder_data is not None
            and self.preorder_data.associated is not None
        )
