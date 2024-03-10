from killbill.client import get_client
from openapi_client import AccountApi
from openapi_client import InvoiceApi
from openapi_client import InvoicePayment
from openapi_client import PaymentApi
from rent.models.lease import Payment


def _make_payment(accountApi: AccountApi, api: PaymentApi, pay: Payment):
    client = pay.client
    account = accountApi.get_account_by_key(external_key=str(client.id))
    if account is None or account.account_id is None:
        return

    invoices = accountApi.get_invoices_for_account(
        account_id=account.account_id)
    print(invoices)

    client = get_client()
    invoiceApi = InvoiceApi(client)
    invoiceApi.create_instant_payment(
        x_killbill_created_by="admin",
        invoice_id=invoices[0].invoice_id,
        invoice_payment=InvoicePayment(
            accountId=account.account_id,
            capturedAmount=float(pay.amount),
        ),
    )


def make_payment(pay: Payment):
    client = get_client()
    account_api = AccountApi(client)
    pay_api = PaymentApi(client)

    _make_payment(account_api, pay_api, pay)
