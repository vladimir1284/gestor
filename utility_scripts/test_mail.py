from django.core.mail import EmailMessage, get_connection
from django.conf import settings

attachment = "utility_scripts/test_mail.py"

with get_connection(
    host=settings.EMAIL_HOST,
    port=settings.EMAIL_PORT,
    username=settings.EMAIL_HOST_USER,
    password=settings.EMAIL_HOST_PASSWORD,
    use_tls=settings.EMAIL_USE_TLS
) as connection:
    subject = "Test"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ["vladimir.rdguez@gmail.com", ]
    message = "Este es un mensaje de prueba"
    msg = EmailMessage(subject, message, email_from,
                       recipient_list, connection=connection)
    msg.attach_file(attachment)
    msg.send()
