from django.conf import settings
from killbill.tools.generate_catalog import sync_catalog
from killbill.tools.sync_accounts import sync_account
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
        api_key={"Killbill_Api_Key": api_key, "Killbill_Api_Secret": api_secret},
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


def update_catalog():
    client = get_client()
    catalog_api = CatalogApi(client)
    sync_catalog(catalog_api)


@receiver(post_save, sender=Lease)
def on_lease_change_create(sender, instance, created, **kwargs):
    update_catalog()


@receiver(post_delete, sender=Lease)
def on_lease_delete(sender, instance, **kwargs):
    update_catalog()
