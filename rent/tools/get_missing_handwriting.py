from rent.models.lease import HandWriting


def get_missing_handwriting(contract) -> list[str]:
    lessee_handwritings = [
        "signature_lessee",
        "date_lessee",
        "date_daniel",
    ]
    missing = []
    for hw in lessee_handwritings:
        if not HandWriting.objects.filter(
            lease=contract,
            position=hw,
        ).exists():
            missing.append(hw)
    return missing
