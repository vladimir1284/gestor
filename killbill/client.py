from django.conf import settings
from killbill.tools.sync_accounts import sync_account
from openapi_client import *


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

    account_api = AccountApi(client)
    sync_account(account_api)
