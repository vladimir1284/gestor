from django.db import models


class Statistics(models.Model):
    """
    Weekly data associated to the date of the sunday (last day of week)
    """
    # Orders
    completed_orders = models.IntegerField()
    gross_income = models.FloatField()
    profit_before_costs = models.FloatField()
    labor_income = models.FloatField()
    discount = models.FloatField()
    third_party = models.FloatField()
    supplies = models.FloatField()

    # Costs
    costs = models.FloatField()

    # Parts
    parts_cost = models.FloatField()
    parts_price = models.FloatField()

    # Payments
    payment_amount = models.FloatField()
    transactions = models.IntegerField()
    # Debt
    debt_created = models.FloatField()
    debt_paid = models.FloatField()
    debt_accumulated = models.FloatField()

    # Sunday after the week
    date = models.DateField()
