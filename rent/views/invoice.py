import tempfile
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string

from rent.models.lease import Due
from rent.models.lease import Lease
from rent.permissions import staff_required


def get_invoice_context(lease_id, date, paid):
    lease = get_object_or_404(Lease, id=lease_id)
    date = datetime.strptime(date, "%m%d%Y")
    due = Due.objects.filter(lease=lease, due_date=date).last()
    context = {"date": date, "lease": lease, "due": due, "paid": (paid == "true")}
    return context


@login_required
def invoice(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    return render(request, "rent/invoice/invoice_view.html", context=context)


def generate_invoice(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    result = generate_invoice_pdf(request, lease_id, date, paid)

    if result is not None:
        # Creating http response
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, "rb")
            response.write(output.read())

        return response
    return None


def generate_invoice_pdf(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    """Generate pdf."""
    image = settings.STATIC_ROOT + "/assets/img/icons/TOWIT.png"
    # Render
    context.setdefault("image", image)
    html_string = render_to_string("rent/invoice/invoice_pdf.html", context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        main_doc = html.render(presentational_hints=True)
        return main_doc.write_pdf()
    return None


INVOICE_DICT = {
    "english": """Dear {}, 

We hope this email finds you well. We would like to thank you for your recent payment. We are pleased to confirm that we have received the payment in full for the attached invoice. 
 
We greatly appreciate your prompt payment, which demonstrates your commitment to our partnership. To ensure timely processing and accurate record-keeping, we have attached the updated invoice for your reference. 
 
Please review the invoice to confirm that all details are accurate. If you have any questions or concerns regarding the invoice, please do not hesitate to contact us. 
 
We value your partnership and look forward to continuing to provide you with exceptional service. If you have any further questions or concerns, please do not hesitate to reach out to us. 
 
Thank you for your business. 
 
Best regards, 

""",
    "spanish": """Estimado {},
 
Esperamos que este correo electrónico te encuentre bien. Nos gustaría agradecerle por su pago reciente. Nos complace confirmar que hemos recibido el pago completo de la factura adjunta.
 
Apreciamos enormemente su pronto pago, lo que demuestra su compromiso con nuestra asociación. Para garantizar un procesamiento oportuno y un mantenimiento de registros preciso, adjuntamos la factura actualizada para su referencia.
 
Revise la factura para confirmar que todos los detalles sean correctos. Si tiene alguna pregunta o inquietud con respecto a la factura, no dude en contactarnos.
 
Valoramos su asociación y esperamos continuar brindándole un servicio excepcional. Si tiene más preguntas o inquietudes, no dude en comunicarse con nosotros.
 
Gracias por hacer negocios.
 
""",
}

PAYMENT_DICT = {
    "english": """Dear {}, 
 
We hope this email finds you well. We would like to kindly remind you that the payment for your leased trailer is due on {}.  
 
As per our agreement, the payment should be made in full by the specified due date. It is essential to ensure timely payment to maintain the smooth operation of your trailer lease.  
 
To facilitate the payment process, we have attached the invoice for your reference. Please review the details and kindly proceed with the payment as soon as possible. 
 
If you have already made the payment, please disregard this reminder. However, if you have any concerns or require assistance, please do not hesitate to reach out to our dedicated customer support team. They will be more than happy to assist you. 
 
Thank you for your prompt attention to this matter. We greatly value your partnership and appreciate your continued business. 
 
""",
    "spanish": """Estimado {},
 
Esperamos que este correo electrónico te encuentre bien. Nos gustaría recordarle que el pago de su remolque arrendado vence el {}.
 
Según nuestro acuerdo, el pago debe realizarse en su totalidad antes de la fecha de vencimiento especificada. Es esencial garantizar el pago puntual para mantener el buen funcionamiento del arrendamiento de su remolque.
 
Para facilitar el proceso de pago, adjuntamos la factura para su referencia. Revise los detalles y proceda con el pago lo antes posible.
 
Si ya realizó el pago, ignore este recordatorio. Sin embargo, si tiene alguna inquietud o necesita ayuda, no dude en comunicarse con nuestro dedicado equipo de atención al cliente. Estarán más que felices de ayudarle.
 
Gracias por su pronta atención, a este asunto. Valoramos enormemente su asociación y apreciamos su continuidad comercial.
 
""",
}

THANKS_DICT = {
    "english": """Best regards, 
 
Daniel Hernández 
TOWIT Houston

Thank you for choosing TOWIT HOUSTON. Follow us at:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Check your invoice attached to this email.""",
    "spanish": """Atentamente,
 
Daniel Hernández 
TOWIT Houston

Gracias por elegir TOWIT HOUSTON. Síganos en:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Google Maps:
goo.gl/maps/GLyCCRaLECF2HcGW8?coh=178571&entry=tt
Vea su factura en el adjunto de este correo.""",
}
DUE_SUBJECT_DICT = {
    "english": "Payment Reminder: Due Date for Leased Trailer",
    "spanish": "Recordatorio de pago: fecha de pago del remolque arrendado",
}
PAID_SUBJECT_DICT = {
    "english": "Invoice from Leased Trailer",
    "spanish": "Factura de la renta del remolque arrendado",
}


@login_required
def send_invoice(request, lease_id, date, paid):
    lease = get_object_or_404(Lease, id=lease_id)
    mail_send_invoice(request, lease_id, date, paid)
    return redirect("client-detail", lease.contract.lessee.id)


def mail_send_invoice(request, lease_id, date, paid):
    if settings.ENVIRONMENT != "production":
        print("Mail virtually sended")
        return

    context = get_invoice_context(lease_id, date, paid)
    if context["lease"].notify:
        client = context["lease"].contract.lessee
        recipient_list = [client.email]
        # if settings.ENVIRONMENT == 'production':
        #     recipient_list = [client.email]
        # else:
        #     recipient_list = ['vladimir.rdguez@gmail.com']

        if paid == "true":
            subject = PAID_SUBJECT_DICT[client.language]
            body = (
                INVOICE_DICT[client.language].format(client)
                + THANKS_DICT[client.language]
            )

        else:
            subject = DUE_SUBJECT_DICT[client.language]
            body = (
                PAYMENT_DICT[client.language].format(
                    client, context["date"].strftime("%m/%d/%Y")
                )
                + THANKS_DICT[client.language]
            )
        try:
            result = generate_invoice_pdf(request, lease_id, date, paid)
            if result:
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False, prefix=f"invoice_rental_{client.id}_"
                ) as output:
                    output.write(result)
                    output.flush()
                    with get_connection(
                        host=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        use_tls=settings.EMAIL_USE_TLS,
                    ) as connection:
                        email_from = settings.EMAIL_HOST_USER
                        msg = EmailMessage(
                            subject,
                            body,
                            email_from,
                            recipient_list,
                            connection=connection,
                        )
                        msg.attach_file(output.name)
                        msg.send()
            else:
                print(body)
        except Exception as e:
            print(e)
