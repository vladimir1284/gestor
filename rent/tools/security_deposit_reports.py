from rent.models.lease import Contract
from rent.models.lease import SecurityDepositDevolution
from rent.tools.adjust_security_deposit import adjust_security_deposit


def security_deposit_reports(ctx: dict, year: int, month: int):
    completed = []
    pendings = []
    actives = []

    total_returned = 0.0
    total_income = 0.0
    total_active = 0.0
    total_pending = 0.0

    # For each active or completed contracts
    contracts = Contract.objects.filter(stage__in=["active", "ended"])
    for contract in contracts:
        # Get contract SecurityDepositDevolution
        _, _, deposit = adjust_security_deposit(contract.id)
        # Already returned
        if deposit.contract.stage == "ended" and deposit.returned:
            # Sub conditional because it does not matter if the returned date does not match
            # to be returned and we will NOT include it in the active list
            if (
                deposit.returned_date is not None
                and deposit.returned_date.year == year
                and deposit.returned_date.month == month
            ):
                completed.append(deposit)
                total_returned += deposit.amount
                total_income += deposit.income
        # Will be returned
        elif deposit.contract.stage == "ended" and deposit.refund_date is not None:
            # Sub conditional because it does not matter if the future returned date does not match
            # to be a pending return and we will NOT include it in the active list
            if deposit.refund_date.year == year and deposit.refund_date.month == month:
                pendings.append(deposit)
                total_pending += deposit.total_deposited_amount
        # is active
        # Just include if it is not a returned or a pending
        # Just include if contract stage is active, not ended
        elif deposit.contract.stage == "active":
            actives.append(deposit)
            total_active += deposit.total_deposited_amount

    ctx["security_actives"] = actives
    ctx["security_completed"] = completed
    ctx["security_pending"] = pendings
    ctx["security_total_active"] = total_active
    ctx["security_total_income"] = total_income
    ctx["security_total_returned"] = total_returned
    ctx["security_total"] = total_active + total_income + total_returned
