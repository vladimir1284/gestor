from killbill.tools.get_lessee import Associated, get_lessee
from openapi_client import Account, AccountApi
from openapi_client.api_client import NotFoundException


def sync_account(account_api: AccountApi):
    lessees = get_lessee()

    for lessee in lessees:
        try:
            account_id = str(lessee.id)
            account_api.get_account_by_key(external_key=account_id)
        except NotFoundException:
            sync_lessee(account_api, lessee)
        except Exception as e:
            print("Error ###########################")
            print(e)


def sync_lessee(account_api: AccountApi, lessee: Associated):
    account_id = str(lessee.id)
    print(f"###### Creating account {account_id}: {lessee.name} ######")
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
    )
    try:
        account_api.create_account("admin", account)
    except Exception as e:
        print(e)
