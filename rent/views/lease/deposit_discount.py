from django.db.transaction import atomic
from django.http import HttpRequest
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.deposit_discount import DepositDiscountForm
from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import Contract
from rent.tools.adjust_security_deposit import adjust_security_deposit
from rent.tools.get_conditions import relativedelta


def get_deposit_discount(contract: Contract):
    discount, _ = DepositDiscount.objects.get_or_create(contract=contract)
    return discount
