from rent.models.lease import HandWriting
from rent.tools.get_conditions import get_rent_conditions_template_from_contract


def get_handwritings(contract, daniel: bool = False) -> list[str]:
    template, version = get_rent_conditions_template_from_contract(contract)

    lessee_handwritings = [
        "signature_lessee",
        "date_lessee",
    ]

    if daniel:
        lessee_handwritings.append("date_daniel")

    if template is not None:
        if template.option(version, "guarantor") == "true":
            lessee_handwritings += [
                "signature_guarantor",
                "date_guarantor",
            ]

        extras = template.option_list(version, "extra_required_sign_date")
        if extras is not None:
            for e in extras:
                if e not in lessee_handwritings:
                    lessee_handwritings.append(e)

    return lessee_handwritings


def get_missing_handwriting(contract) -> list[str]:
    lessee_handwritings = get_handwritings(contract)

    missing = []
    for hw in lessee_handwritings:
        if not HandWriting.objects.filter(
            lease=contract,
            position=hw,
        ).exists():
            missing.append(hw)
    return missing


def check_handwriting(contract, daniel: bool = True) -> bool:
    lessee_handwritings = get_handwritings(contract, daniel)

    for hw in lessee_handwritings:
        if not HandWriting.objects.filter(
            lease=contract,
            position=hw,
        ).exists():
            return False
    return True
