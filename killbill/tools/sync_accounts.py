from killbill.tools.get_lessee import Associated
from killbill.tools.get_lessee import get_lessee
from openapi_client import Account
from openapi_client import AccountApi
from openapi_client.api_client import NotFoundException
from rent.models.lease import LesseeData


def sync_account(account_api: AccountApi):
    lessees = get_lessee()

    for lessee in lessees:
        try:
            account_id = str(lessee.id)
            account = account_api.get_account_by_key(external_key=account_id)
            if account is None or account.account_id is None:
                continue
            update_account(account_api, account, lessee)
        except NotFoundException:
            sync_lessee(account_api, lessee)
        except Exception as e:
            print("Error ###########################")
            print(e)


def update_account(account_api: AccountApi, account: Account, lessee: Associated):
    print(
        f"###### Updating account {account.account_id} -> {lessee.id}: {lessee.name} ######"
    )
    lesseeData = LesseeData.objects.filter(associated=lessee).first()
    account.name = lessee.name
    account.first_name_length = len(lessee.name)
    account.email = lessee.email
    account.city = lessee.city
    account.state = lessee.state
    account.phone = lessee.phone_number.__str__()
    account.currency = "USD"
    account.time_zone = "Etc/UTC"
    account.country = "US"
    account.locale = "en_US"
    account.address1 = (
        lesseeData.client_address if lesseeData is not None else "No Address"
    )
    account.address2 = ""
    account.postal_code = "123456"
    account.company = "TOWIT"

    account_api.update_account_without_preload_content(
        account_id=account.account_id,
        x_killbill_created_by="admin",
        account=account,
    )


def sync_lessee(account_api: AccountApi, lessee: Associated):
    account_id = str(lessee.id)
    print(f"###### Creating account {account_id}: {lessee.name} ######")
    lesseeData = LesseeData.objects.filter(associated=lessee).first()
    account = Account(
        name=lessee.name,
        firstNameLength=len(lessee.name),
        externalKey=account_id,
        email=lessee.email,
        city=lessee.city,
        state=lessee.state,
        phone=lessee.phone_number.__str__(),
        currency="USD",
        timeZone="Etc/UTC",
        country="US",
        locale="en_US",
        address1=lesseeData.client_address if lesseeData is not None else "No Address",
        address2="",
        postalCode="123456",
        company="TOWIT",
    )
    try:
        account_api.create_account("admin", account)
    except Exception as e:
        print(e)
