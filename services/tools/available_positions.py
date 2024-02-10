from django.db.models import Q
from utils.models import (
    Order,
)


def get_available_positions(
    storage: bool = True, null: bool = False, current_pos: int | None = None
):
    options = []
    for i in range(1, 9):
        if (
            not Order.objects.filter(
                Q(position=i),
                Q(Q(status="pending") | Q(status="processing"))
                | Q(Q(status="complete") | Q(status="payment_pending")),
            ).exists()
            or i == current_pos
        ):
            options.append((i, f"Position {i}"))

    if storage:
        options.append((0, "Storage"))

    if null:
        options.append((None, "Null"))

    return options
