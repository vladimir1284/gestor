from rent.models.lease import HandWriting
from rent.tools.get_conditions import \
    get_rent_conditions_template_from_contract

DEFAULT_LESSEE_SIGNATURES = [
    "signature_lessee",
    "date_lessee",
]

DEFAULT_GUARANTOR_SIGNATURES = [
    "signature_guarantor",
    "date_guarantor",
]


def get_handwritings(contract, daniel: bool = False) -> list[str]:
    template, version = get_rent_conditions_template_from_contract(contract)

    if daniel:
        lessee_handwritings = ["date_daniel"]
    else:
        lessee_handwritings = []

    lessee_handwritings += DEFAULT_LESSEE_SIGNATURES

    if template is not None:
        if template.option(version, "guarantor") == "true":
            lessee_handwritings += DEFAULT_GUARANTOR_SIGNATURES

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


def is_valid_as_next(mhw: str | None, is_guarantor: bool) -> bool:
    if mhw is None or mhw == "date_daniel":
        return False

    return (not is_guarantor and mhw in DEFAULT_LESSEE_SIGNATURES) or (
        is_guarantor and mhw in DEFAULT_GUARANTOR_SIGNATURES
    )


def get_valid_next(contract, is_guarantor: bool) -> str | None:
    missing_hws = get_missing_handwriting(contract)
    mhw = None

    # Get the first valid to change
    while len(missing_hws) > 0 and not is_valid_as_next(mhw, is_guarantor):
        mhw = missing_hws.pop(0)

    # if exists capture
    if is_valid_as_next(mhw, is_guarantor):
        return mhw

    return None
