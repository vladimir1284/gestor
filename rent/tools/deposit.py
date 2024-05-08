import logging
import tempfile

import jwt
import qrcode.image.svg
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import datetime
from django.utils.timezone import timedelta
from django.utils.timezone import timezone

from rent.models.trailer_deposit import TrailerDeposit
from rent.views.vehicle import getImages

MULTILANG_BODY = {
    "english": """Dear {}, your vehicle at TOWITHOUSTON is reserved!
Due: ${}
Check the file attached to this email.
You can make your payment using Zelle by registering the e-mail: towitrepairs@gmail.com owned by Towit Repairs LLC
For Cash App, please register the user $towithouston owned by Daniel Hernández
You can also pay with credit or debit card with an extra fee of 3% for the Square platform
We also accept cash
Thanks""",
    "spanish": """Estimado {}, su vehículo en TOWITHOUSTON está reservado!
Total a pagar: ${}
Ver detalles en el adjunto de este correo
Para realizar el pago a través de Zelle registre el correo: towitrepairs@gmail.com le aparecerá la cuenta a nombre de Towit Repairs LLC
Para realizar el pago via Cash App registre el usuario $towithouston le aparecerá la cuenta a nombre de Daniel Hernández
Puede pagar con targeta de credito o debito con un recargo del 3% de la plataforma Square
Además aceptamos efectivo
Gracias""",
}


def trailer_deposit_context(request, id):
    deposit: TrailerDeposit = get_object_or_404(TrailerDeposit, id=id)
    images, pinned_image = getImages(deposit.trailer)

    exp = datetime.now(timezone.utc) + timedelta(hours=2)
    tokCtx = {
        "deposit_id": id,
        "exp": exp,
    }

    token = jwt.encode(tokCtx, settings.SECRET_KEY, algorithm="HS256")

    url_base = "{}://{}".format(request.scheme, request.get_host())
    url = url_base + reverse("trailer-deposit-conditions", args=[token])
    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=20,
    )

    context = {
        "deposit": deposit,
        "images": images,
        "pinned_image": pinned_image,
        "equipment": deposit.trailer,
        "qr_url": img.to_string(encoding="unicode"),
        "url": url,
        "token": token,
    }
    return context


def trailer_deposit_conditions_pdf(request, id):
    context = trailer_deposit_context(request, id)
    context["pdf"] = True
    html_string = render_to_string(
        "rent/trailer_deposit_conditions.html",
        context,
    )
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        return html.write_pdf()
    return None


def send_deposit_pdf(request, deposit: TrailerDeposit):
    client = deposit.client

    email = client.email
    if email is None or email == "":
        logging.warn("client has not email")
        return

    body = MULTILANG_BODY[client.language].format(
        client.name,
        int(deposit.amount),
    )
    try:
        if settings.ENVIRONMENT != "production":
            print(body)
            return

        result = trailer_deposit_conditions_pdf(request, deposit.id)
        if result is None:
            return

        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False, prefix=f"reservation_towit_{deposit.id}_"
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
                    [email],
                    connection=connection,
                )
                msg.attach_file(output.name)
                msg.send()
    except Exception as e:
        logging.critical(e)
