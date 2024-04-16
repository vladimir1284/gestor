import inspect
import time
from datetime import datetime
from datetime import timedelta
from threading import Thread

from django.db import models
from django.dispatch import receiver

from costs.models import Cost
from dashboard.tools.calculate_stats import calculate_stats
from inventory.models import ProductTransaction
from rent.models.lease import LeaseDeposit
from rent.models.lease import SecurityDepositDevolution
from services.models import Expense
from services.models import Payment
from services.models import PendingPayment
from services.models import ServiceTransaction
from utils.models import Order
from utils.models import Statistics

Queue = []


def week_stats_recal(date):
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=7)
    print(start_date, end_date)

    # Calcula las estadísticas de la semana
    stats, _ = Statistics.objects.get_or_create(date=end_date)

    calculate_stats(stats, start_date, end_date)


def _recalculator():
    while True:
        if len(Queue) > 0:
            date = Queue.pop(0)
            try:
                if isinstance(date, str):
                    date = datetime.strptime(date, "%m%d%Y").date()
                print("Recal Statistics", date)
                week_stats_recal(date)
            except Exception as e:
                print(e)
        else:
            time.sleep(5)


def initRecalculator():
    task = Thread(target=_recalculator)
    task.daemon = True
    task.start()
    # loop = asyncio.get_event_loop()
    # loop.create_task(_recalculator())


def pushRecal(date):
    if date is None or date in Queue:
        return
    if not isinstance(date, str):
        try:
            if (
                hasattr(date, "day")
                and hasattr(date, "month")
                and hasattr(date, "year")
            ):
                d = date.day() if inspect.ismethod(date.day) else date.day
                m = date.month() if inspect.ismethod(date.month) else date.month
                y = date.year() if inspect.ismethod(date.year) else date.year
                date = f"{m:02}{d:02}{y:04}"
        except Exception as e:
            print(e)
    Queue.append(date)


def on_change_order_process(instance: Order):
    if instance is None:
        return

    if instance.status != "complete" or instance.type != "sell":
        return

    if instance.associated is not None and instance.associated.membership:
        return

    pushRecal(instance.terminated_date)


@receiver(models.signals.post_save, sender=Order)
def on_change_order(sender, instance: Order, created, **kwargs):
    on_change_order_process(instance)


@receiver(models.signals.post_save, sender=Cost)
def on_change_cost(sender, instance: Cost, created, **kwargs):
    pushRecal(instance.date)


@receiver(models.signals.post_save, sender=PendingPayment)
def on_change_pendpay(sender, instance: PendingPayment, created, **kwargs):
    pushRecal(instance.created_date)


@receiver(models.signals.post_save, sender=Payment)
def on_change_pay(sender, instance: Payment, created, **kwargs):
    on_change_order_process(instance.order)


@receiver(models.signals.post_save, sender=LeaseDeposit)
def on_change_lease_dep(sender, instance: LeaseDeposit, created, **kwargs):
    pushRecal(instance.date)


@receiver(models.signals.post_save, sender=SecurityDepositDevolution)
def on_change_sec_dep_ret(
    sender, instance: SecurityDepositDevolution, created, **kwargs
):
    pushRecal(instance.returned_date)


@receiver(models.signals.post_save, sender=ProductTransaction)
def on_change_prod_trans(sender, instance: ProductTransaction, created, **kwargs):
    on_change_order_process(instance.order)


@receiver(models.signals.post_save, sender=Expense)
def on_change_expense(sender, instance: Expense, created, **kwargs):
    on_change_order_process(instance.order)


@receiver(models.signals.post_save, sender=ServiceTransaction)
def on_change_ser_trans(sender, instance: ServiceTransaction, created, **kwargs):
    on_change_order_process(instance.order)
