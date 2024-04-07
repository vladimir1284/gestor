from django.conf import settings
from twilio.rest import Client

CONTACT_FORM_URL = {
    "english": """Please, complete the form in {}.""",
    "spanish": """Por favor, complete el formulario en {}.""",
}


def sendSMSLesseeContactURL(to: str, url: str, lang: str = "spanish"):
    body = CONTACT_FORM_URL[lang].format(url)
    sendSMS(to, body)


def sendSMS(to: str, body: str):
    if settings.ENVIRONMENT == "production":
        sms_client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        message = sms_client.messages.create(
            body=body,
            from_="+13203563490",
            to=str(to),
        )
        print(message.sid)
    else:
        print(body)
