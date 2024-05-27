from rent.models.trailer_deposit import TrailerDeposit
from rent.models.trailer_deposit import TrailerDepositTrace


def deposits_on_hold_reports(ctx: dict, year: int, month: int):
    on_hold = TrailerDeposit.objects.filter(
        cancelled=False,
        done=False,
        date__year=year,
        date__month=month,
    )
    ctx["deposits_on_hold"] = on_hold
    ctx["deposits_on_hold_count"] = on_hold.count()

    sum = 0
    for d in on_hold:
        sum += d.amount
    ctx["deposits_on_hold_total"] = sum


def deposits_security_reports(ctx: dict, year: int, month: int):
    security = TrailerDeposit.objects.filter(
        cancelled=False,
        done=True,
        date__year=year,
        date__month=month,
    )
    ctx["deposits_security"] = security
    ctx["deposits_security_count"] = security.count()

    sum = 0
    for d in security:
        sum += d.amount
    ctx["deposits_security_total"] = sum


def deposits_renovations_reports(ctx: dict, year: int, month: int):
    renovations = TrailerDepositTrace.objects.filter(
        status="renovated",
        created_at__year=year,
        created_at__month=month,
    ).order_by("-created_at")
    deposits_renovations = {}
    for r in renovations:
        inv = r.trailer_deposit.invoice_num
        if inv not in deposits_renovations:
            deposits_renovations[inv] = r.trailer_deposit
            deposits_renovations[inv].renovations = [r]
        else:
            deposits_renovations[inv].renovations.append(r)

    ctx["deposits_renovations"] = deposits_renovations
    ctx["deposits_renovations_count"] = renovations.count()
    sum = 0
    for r in renovations:
        sum += r.amount
    ctx["deposits_renovations_total"] = sum


def deposits_finished_reports(ctx: dict, year: int, month: int):
    ended = TrailerDeposit.objects.filter(
        cancelled=True,
        done=False,
        date__year=year,
        date__month=month,
    )
    ctx["deposits_finished"] = ended
    ctx["deposits_finished_count"] = ended.count()

    total = 0
    income = 0
    returned = 0
    for d in ended:
        total += d.amount
        income += d.income
        returned += d.returned
    ctx["deposits_finished_total"] = total
    ctx["deposits_finished_income"] = income
    ctx["deposits_finished_returned"] = returned


def deposits_reports(ctx: dict, year: int, month: int):
    deposits_on_hold_reports(ctx, year, month)
    deposits_security_reports(ctx, year, month)
    deposits_renovations_reports(ctx, year, month)
    deposits_finished_reports(ctx, year, month)

    ctx["deposits_total"] = (
        ctx["deposits_on_hold_total"]
        + ctx["deposits_security_total"]
        + ctx["deposits_renovations_total"]
        + ctx["deposits_finished_total"]
    )
