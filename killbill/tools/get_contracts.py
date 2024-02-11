from rent.models.lease import Contract


def get_contracts() -> list[Contract]:
    contracts = Contract.objects.filter(stage="active").order_by(
        "lessee__name", "lessee__alias"
    )
    return contracts
