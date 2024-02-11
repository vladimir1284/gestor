from killbill.tools.generate_catalog import get_period
from openapi_client import AccountApi, Subscription, SubscriptionApi
from openapi_client.exceptions import NotFoundException
from rent.models.lease import Associated, Lease


def subscribe(
    sub_api: SubscriptionApi,
    accountID: str,
    period: str,
    price: float,
    product: str = "TrailerRent",
    priceList: str = "DEFAULT",
):
    price_name = "{:.2f}".format(price)
    price_name = price_name.replace(".", "-")
    plan_name = f"{product}-{period}-{price_name}".lower()
    external_key = f"{accountID}-{plan_name}"

    try:
        sub_api.get_subscription_by_key(external_key=external_key)
        print(
            f"EXISTING SUBSCRIPTION [{external_key}] #################################"
        )
    except NotFoundException:
        print(
            f"SUBSCRIPTION [{external_key}] #################################")

        subscription = Subscription(
            externalKey=external_key,
            accountId=accountID,
            productName=product,
            billingPeriod=period,
            priceList=priceList,
            planName=plan_name,
        )
        sub_api.create_subscription_without_preload_content(
            "admin", subscription)
    except Exception as e:
        print(e)


def unsubscribe(
    sub_api: SubscriptionApi,
    accountID: str,
    period: str,
    price: float,
    product: str = "TrailerRent",
):
    price_name = "{:.2f}".format(price)
    price_name = price_name.replace(".", "-")
    plan_name = f"{product}-{period}-{price_name}".lower()
    external_key = f"{accountID}-{plan_name}"

    try:
        subscription = sub_api.get_subscription_by_key(
            external_key=external_key,
        )
        if subscription.subscription_id is None:
            print(
                f"UNEXISTING SUBSCRIPTION [{external_key}] #################################"
            )
            return
        sub_api.cancel_subscription_plan(
            subscription_id=subscription.subscription_id,
            x_killbill_created_by="admin",
        )
        print(
            f"UNSUBSCRIVE [{external_key}] #################################")
    except NotFoundException:
        print(
            f"UNEXISTING SUBSCRIPTION [{external_key}] #################################"
        )
    except Exception as e:
        print(e)


def cancel_unsubscribe(
    sub_api: SubscriptionApi,
    accountID: str,
    period: str,
    price: float,
    product: str = "TrailerRent",
):
    price_name = "{:.2f}".format(price)
    price_name = price_name.replace(".", "-")
    plan_name = f"{product}-{period}-{price_name}".lower()
    external_key = f"{accountID}-{plan_name}"

    try:
        subscription = sub_api.get_subscription_by_key(
            external_key=external_key,
        )
        if subscription.subscription_id is None:
            print(
                f"UNEXISTING SUBSCRIPTION [{external_key}] #################################"
            )
            return
        sub_api.uncancel_subscription_plan(
            subscription_id=subscription.subscription_id,
            x_killbill_created_by="admin",
        )
        print(
            f"CANCEL UNSUBSCRIPTION [{external_key}] #################################"
        )
    except NotFoundException:
        print(
            f"UNEXISTING SUBSCRIPTION [{external_key}] #################################"
        )
    except Exception as e:
        print(e)


def subscribe_associated(
    sub_api: SubscriptionApi,
    account_api: AccountApi,
    associated: Associated,
    lease: Lease,
):
    period = get_period(lease.payment_frequency.__str__())
    price = lease.payment_amount
    account_id = str(associated.id)

    account = account_api.get_account_by_key(external_key=account_id)

    if account.account_id is None:
        return

    subscribe(
        sub_api=sub_api,
        accountID=account.account_id,
        period=period,
        price=price,
    )


def unsubscribe_associated(
    sub_api: SubscriptionApi,
    account_api: AccountApi,
    associated: Associated,
    lease: Lease,
):
    period = get_period(lease.payment_frequency.__str__())
    price = lease.payment_amount
    account_id = str(associated.id)

    account = account_api.get_account_by_key(external_key=account_id)

    if account.account_id is None:
        return

    unsubscribe(
        sub_api=sub_api,
        accountID=account.account_id,
        period=period,
        price=price,
    )


def cancel_unsubscribe_associated(
    sub_api: SubscriptionApi,
    account_api: AccountApi,
    associated: Associated,
    lease: Lease,
):
    period = get_period(lease.payment_frequency.__str__())
    price = lease.payment_amount
    account_id = str(associated.id)

    account = account_api.get_account_by_key(external_key=account_id)

    if account.account_id is None:
        return

    cancel_unsubscribe(
        sub_api=sub_api,
        accountID=account.account_id,
        period=period,
        price=price,
    )
