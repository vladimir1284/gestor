from collections import defaultdict
from datetime import timedelta
from math import ceil

import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from num2words import num2words

from rent.models.lease import Contract
from rent.models.lease import HandWriting
from rent.models.lease import Inspection
from rent.models.lease import LesseeData
from rent.models.lease import Tire
from rent.models.trailer_deposit import TrailerDeposit
from rent.views.calendar import datetime


def get_contract(id):
    contract = Contract.objects.get(id=id)
    try:
        contract.inspection = Inspection.objects.get(lease=contract)
    except Inspection.DoesNotExist:
        contract.inspection = None
    if contract.contract_type == "lto":
        contract.n_payments = ceil(
            (contract.total_amount - contract.security_deposit)
            / contract.payment_amount
        )
        contract.contract_end_date = contract.effective_date + timedelta(
            days=contract.contract_term * 30
        )
    else:
        contract.contract_end_date = contract.effective_date + timedelta(
            days=contract.contract_term * 30
        )
    contract.lessee.data = LesseeData.objects.filter(associated=contract.lessee).last()
    return contract


def prepare_contract_view(id):
    contract = get_contract(id)
    on_hold = TrailerDeposit.objects.filter(contract=contract).last()
    signatures = HandWriting.objects.filter(lease=contract)
    context = {
        "contract": contract,
        "on_hold": on_hold,
    }
    if contract.renovation_term:
        if contract.renovation_term == 1:
            context["renovation_term_every"] = "month-to-month"
            context["renovation_term_num"] = (
                num2words(contract.renovation_term, lang="en") + " month"
            )
        else:
            context["renovation_term_every"] = (
                "every " + num2words(contract.renovation_term, lang="en") + " months"
            )
            context["renovation_term_num"] = (
                num2words(contract.renovation_term, lang="en") + " months"
            )
    for sign in signatures:
        context.setdefault(sign.position, sign)
    # Inspection tires sumamry
    tires = Tire.objects.filter(inspection=contract.inspection)
    # Create a defaultdict to store the count of tires for each remaining life
    remaining_life_counts = defaultdict(int)

    # Iterate over the tires queryset and count the remaining life for each group
    for tire in tires:
        remaining_life_counts[tire.remaining_life] += 1

    context.setdefault("remaining_life_counts", dict(remaining_life_counts))
    return context


def get_contract_token(id):
    exp = datetime.utcnow() + timedelta(hours=2)
    context = {
        "contract": id,
        "exp": exp,
    }

    token = jwt.encode(context, settings.SECRET_KEY, algorithm="HS256")
    return token
