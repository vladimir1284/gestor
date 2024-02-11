from django.conf import settings
from killbill.tools.generate_catalog import get_leases, sync_catalog
from killbill.tools.subscriptions import subscribe_associated, unsubscribe_associated
from killbill.tools.sync_accounts import sync_account, sync_lessee
from openapi_client import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rent.models.lease import Lease


def get_client():
    baseURL = settings.KILLBILL_BASE_URL
    api_key = settings.KILLBILL_API_KEY
    api_secret = settings.KILLBILL_API_SECRET
    username = settings.KILLBILL_USERNAME
    password = settings.KILLBILL_PASSWORD

    config = Configuration(
        host=baseURL,
        api_key={"Killbill_Api_Key": api_key,
                 "Killbill_Api_Secret": api_secret},
        username=username,
        password=password,
    )
    client = ApiClient(config)
    return client


def execute_sync():
    client = get_client()

    # catalog_api = CatalogApi(client)
    # sync_catalog(catalog_api)

    account_api = AccountApi(client)
    sync_account(account_api)

    sub_api = SubscriptionApi(client)

    leases = get_leases()
    for lease in leases:
        if lease.contract is None or lease.contract.lessee is None:
            continue

        associated = lease.contract.lessee
        try:
            subscribe_associated(
                account_api=account_api,
                sub_api=sub_api,
                associated=associated,
                lease=lease,
            )
        except Exception as e:
            print(e)


def update_catalog(client):
    catalog_api = CatalogApi(client)
    sync_catalog(catalog_api)


@receiver(post_save, sender=Lease)
def on_lease_change_create(sender, instance: Lease, created, **kwargs):
    client = get_client()
    update_catalog(client)

    if instance.contract is None or instance.contract.lessee is None:
        return

    # Get api
    sub_api = SubscriptionApi(client)
    account_api = AccountApi(client)
    # Get associated
    associated = instance.contract.lessee

    if created:
        # Add account
        sync_lessee(account_api, associated)
        # Subscribe it
        subscribe_associated(sub_api, account_api, associated, instance)
    elif instance.contract.stage != "active":
        unsubscribe_associated(sub_api, account_api, associated, instance)


@receiver(post_delete, sender=Lease)
def on_lease_delete(sender, instance: Lease, **kwargs):
    client = get_client()
    update_catalog(client)

    if instance.contract is not None and instance.contract.lessee is not None:
        associated = instance.contract.lessee
        sub_api = SubscriptionApi(client)
        account_api = AccountApi(client)
        unsubscribe_associated(sub_api, account_api, associated, instance)


# @receiver(post_save, sender=Associated)
# def on_associated_change_create(sender, instance, created, **kwargs):
#     if created:
#         client = get_client()
#         account_api = AccountApi(client)
#         sync_lessee(account_api, instance)
