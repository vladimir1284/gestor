from rent.models.lease import Contract
from rent.models.lease import SecurityDepositDevolution
from rent.tools.adjust_security_deposit import adjust_security_deposit


def security_deposit_reports(ctx: dict, year: int, month: int):
    completed = SecurityDepositDevolution.objects.filter(
        returned_date__year=year,
        returned_date__month=month,
        returned=True,
    )

    total_returned = 0.0
    total_income = 0.0
    total_active = 0.0

    completed_contracts = []
    for c in completed:
        total_returned += c.amount
        total_income += c.income
        if c.contract.id not in completed_contracts:
            completed_contracts.append(c.contract.id)

    contracts = Contract.objects.exclude(
        id__in=completed_contracts,
    ).exclude(
        stage__in=["ended", "gaarbage"],
    )
    actives = []
    for c in contracts:
        _, _, deposit = adjust_security_deposit(c.id)
        actives.append(deposit)
        total_active += deposit.total_deposited_amount

    ctx["security_actives"] = actives
    ctx["security_completed"] = completed
    ctx["security_total_active"] = total_active
    ctx["security_total_income"] = total_income
    ctx["security_total_returned"] = total_returned
    ctx["security_total"] = total_active + total_income + total_returned
