from killbill.client import get_client
from openapi_client import AccountApi
from openapi_client import ApiClient
from openapi_client import InvoiceApi
from openapi_client import InvoicePayment
from openapi_client import PaymentApi
from rent.models.lease import Payment


def _make_payment(apiClient: ApiClient, pay: Payment):
    accountApi = AccountApi(apiClient)
    PaymentApi(apiClient)
    invoiceApi = InvoiceApi(apiClient)

    client = pay.client
    account = accountApi.get_account_by_key(external_key=str(client.id))
    if account is None or account.account_id is None:
        return

    invoices = accountApi.get_invoices_for_account(
        account_id=account.account_id,
        unpaid_invoices_only=True,
        # include_invoice_components=True,
    )
    print("###################################")
    print(invoices)
    if len(invoices) == 0:
        return

    invoice = invoiceApi.get_invoice(
        invoice_id=invoices[-1].invoice_id,
    )
    print("===================================")
    print(invoice)

    client = get_client()
    invoiceApi = InvoiceApi(client)
    invoice_pay = invoiceApi.create_instant_payment_without_preload_content(
        x_killbill_created_by="admin",
        invoice_id=invoices[-1].invoice_id,
        external_payment=True,
        invoice_payment=InvoicePayment(
            accountId=account.account_id,
            authAmount=float(pay.amount),
            capturedAmount=float(pay.amount),
            purchasedAmount=float(pay.amount),
        ),
    )
    print("###################################")
    print(invoice_pay)

    # paymentApi.capture_authorization(
    #     payment_id=invoice_pay.payment_id,
    #     x_killbill_created_by="admin",
    #     payment_transaction=PaymentTransaction(
    #         paymentId=invoice_pay.payment_id,
    #         amount=invoice_pay.captured_amount,
    #         processedAmount=invoice_pay.captured_amount,
    #     ),
    # )


def make_payment(pay: Payment):
    client = get_client()
    _make_payment(client, pay)
