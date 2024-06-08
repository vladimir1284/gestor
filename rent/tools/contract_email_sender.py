from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import get_connection

CONTRACT_SIGNATURE_SUBJECT = {
    "english": "Contract signature",
    "spanish": "Firma de contrato",
}

CONTRACT_SIGNATURE_BODY = {
    "english": """Dear {},
 
We hope this email finds you well.

In order to complete the contract, your signature is required at the following URL:

{}
 
Thank you for choosing TOWIT HOUSTON. Follow us at:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Check your invoice attached to this email.""",
    "spanish": """Estimado {},
 
Esperamos que este correo electrónico te encuentre bien.

Para completar el contrato es necesario su firma en la siguiente URL:

{}

Gracias por elegir TOWIT HOUSTON. Síganos en:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Google Maps:
goo.gl/maps/GLyCCRaLECF2HcGW8?coh=178571&entry=tt
""",
}


def contract_email_send_sign_url(
    email: str,
    name: str,
    url: str,
    lang: str = "english",
):
    if settings.ENVIRONMENT != "production":
        print(f"Email send to {email}")
        return

    recipient_list = [email]

    subject = CONTRACT_SIGNATURE_SUBJECT[lang]
    body = CONTRACT_SIGNATURE_BODY[lang].format(name, url)

    try:
        with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        ) as connection:
            email_from = settings.EMAIL_HOST_USER
            msg = EmailMessage(
                subject, body, email_from, recipient_list, connection=connection
            )
            msg.send()
    except Exception as e:
        print(e)
