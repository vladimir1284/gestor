from services.models import Order, OrderSignature
from django.template.loader import render_to_string
from django.conf import settings
import tempfile
from django.core.mail import EmailMessage, get_connection


def conditions_to_pdf(request, order_id):
    order = Order.objects.get(id=order_id)
    client = order.associated
    # client = Associated.objects.get(id=client_id)

    signature = OrderSignature.objects.filter(
        associated=client).order_by("date").last()

    context = {
        "signature": signature.img.url,
        "client": str(client),
    }
    html_string = render_to_string("services/conditions_to_pdf.html", context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        return html.write_pdf()
        # main_doc = html.render(presentational_hints=False)
        # return main_doc.write_pdf()
    return None


def send_pdf_conditions_to_email(request, order_id, recipient_list):
    body = "CONDICIONES DE SERVICIO"
    try:
        if settings.ENVIRONMENT == "production":
            result = conditions_to_pdf(request, order_id)
            if result:
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False, prefix=f"invoice_towit_{order_id}_"
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
                        subject = "Towit Houston"
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
