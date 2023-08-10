from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .sms import DEBT_REMINDER
import tempfile
from services.models import Payment
from django.template.loader import render_to_string

PAYMENT_DICT = {
    'english':
    """Dear {}, your vehicle at TOWITHOUSTON is ready!
Due: ${}
Check the file attached to this email.
You can make your payment using Zelle by registering the e-mail: towitrepairs@gmail.com owned by Towit Repairs LLC
For Cash App, please register the user $towithouston owned by Daniel Hernández
You can also pay with credit or debit card with an extra fee of 3% for the Square platform
We also accept cash
Thanks""",
    'spanish':
    """Estimado {}, su vehículo en TOWITHOUSTON está listo!
Total a pagar: ${}
Ver detalles en el adjunto de este correo
Para realizar el pago a través de Zelle registre el correo: towitrepairs@gmail.com le aparecerá la cuenta a nombre de Towit Repairs LLC
Para realizar el pago via Cash App registre el usuario $towithouston le aparecerá la cuenta a nombre de Daniel Hernández
Puede pagar con targeta de credito o debito con un recargo del 3% de la plataforma Square
Además aceptamos efectivo
Gracias"""
}

THANKS_DICT = {
    'english':
    """Thank you for choosing TOWIT. Follow us at:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Check your invoice attached to this email.""",
    'spanish':
    """Gracias por elegir TOWITHOUSTON. Síganos en:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Google Maps:
goo.gl/maps/GLyCCRaLECF2HcGW8?coh=178571&entry=tt
Vea su factura en el adjunto de este correo."""
}


def mail_send_invoice(context,
                      request,
                      recipient_list):
    order = context['order']
    client = order.associated
    if client:
        if order.status == "complete":
            body = THANKS_DICT[client.language].format(order.id)
            payments = Payment.objects.filter(order=order)
            for payment in payments:
                if payment.category.name == 'debt':
                    body += "\n" + \
                        DEBT_REMINDER[client.language].format(payment.amount)
                    break
        else:
            from .order import computeOrderAmount
            computeOrderAmount(order)
            body = PAYMENT_DICT[client.language].format(
                client.name,
                int(order.amount + order.tax), order.id)
        try:
            if settings.ENVIRONMENT == 'production':
                result = generate_invoice_pdf(context, request)
                if result:
                    with tempfile.NamedTemporaryFile(
                            suffix=".pdf",
                            delete=False,
                            prefix=F"invoice_towit_{order.id}_") as output:
                        output.write(result)
                        output.flush()
                        with get_connection(
                            host=settings.EMAIL_HOST,
                            port=settings.EMAIL_PORT,
                            username=settings.EMAIL_HOST_USER,
                            password=settings.EMAIL_HOST_PASSWORD,
                            use_tls=settings.EMAIL_USE_TLS
                        ) as connection:
                            subject = "Towit Houston"
                            email_from = settings.EMAIL_HOST_USER
                            msg = EmailMessage(subject, body, email_from,
                                               recipient_list, connection=connection)
                            msg.attach_file(output.name)
                            msg.send()
            else:
                print(body)
        except Exception as e:
            print(e)


def sendMail(context, request, address, send_copy=False):
    invoice = generate_invoice_pdf(context, request)
    recipient_list = [address]
    if send_copy:
        recipient_list.append('info@towithouston.com')
    mail_send_invoice(context, request, recipient_list)


def generate_invoice_pdf(context, request):
    """Generate pdf."""
    image = settings.STATIC_ROOT+'/assets/img/icons/TOWIT.png'
    # Render
    context.setdefault('image', image)
    html_string = render_to_string('services/invoice_pdf.html', context)
    if settings.ENVIRONMENT == 'production':
        from weasyprint import HTML
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        main_doc = html.render(presentational_hints=True)
        return main_doc.write_pdf()
    return None
