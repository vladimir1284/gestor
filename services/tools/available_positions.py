from django.db.models import Q

from utils.models import (
    Order,
)


def get_available_positions(
    storage: bool = True,
    null: bool = False,
    current_pos: int | None = None,
    availables: bool = False,
    just_current_pos: bool = False,
    invert_order: bool = False,
):
    options = []
    availables_pos = False

    if invert_order:
        if null:
            options.append((None, "Outside"))
        if storage:
            options.append((0, "Storage"))

    if not just_current_pos:
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
                availables_pos = True
    elif current_pos is not None and current_pos != 0:
        options.append((current_pos, f"Position {current_pos}"))
        availables_pos = True

    if not invert_order:
        if storage:
            options.append((0, "Storage"))
        if null:
            options.append((None, "Outside"))

    if availables:
        return options, availables_pos
    return options
