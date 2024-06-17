from django.conf import settings
from twilio.rest import Client

NUM_PREFIX = "whatsapp:"


def send_whatsapp(to: str, body: str):
    client = Client(settings.TWILIO_WHATSAPP_SID, settings.TWILIO_WHATSAPP_TOKEN)
    client.messages.create(
        to=NUM_PREFIX + to,
        from_=NUM_PREFIX + settings.TWILIO_WHATSAPP_NUM,
        body=body,
    )
    print(f"Whatsapp message send to: {to}\nWith body: {body}")
