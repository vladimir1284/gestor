from twilio.rest import Client
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    redirect,
    get_object_or_404,
)

from services.models import Order, Payment

PAYMENT_DICT = {
    'english':
    """Dear {}, your vehicle at TOWITHOUSTON is ready!
Due: ${}
Check the following link for details: towit.pythonanywhere.com/services/pdf-invoice/{}
You can make your payment using Zelle by registering the e-mail: towitrepairs@gmail.com owned by Towit Repairs LLC
For Cash App, please register the user $towithouston owned by Daniel Hernández
You can also pay with credit or debit card with an extra fee of 3% for the Square platform
We also accept cash
Thanks""",
    'spanish':
    """Estimado {}, su vehículo en TOWITHOUSTON está listo!
Total a pagar: ${}
Ver detalles en el siguiente enlace: towit.pythonanywhere.com/services/pdf-invoice/{}
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
Check your invoice at the following link: towit.pythonanywhere.com/services/pdf-invoice/{}""",
    'spanish':
    """Gracias por elegir TOWITHOUSTON. Síganos en:
TikTok:
www.tiktok.com/@towithouston
Facebook:
www.facebook.com/towithouston
Google Maps:
goo.gl/maps/GLyCCRaLECF2HcGW8?coh=178571&entry=tt
Vea su factura en el siguiente enlace: towit.pythonanywhere.com/services/pdf-invoice/{}"""
}

DEBT_REMINDER = {
    'english':
    """You have a pending payment of ${}.
Remember that your deadline will be in 15 days!""",
    'spanish':
    """Usted quedó debiendo ${}. 
Recuerde que tiene 15 días para pagarlo!"""
}


def twilioSendSMS(order: Order, status: str):
    client = order.associated
    if client:
        if status == "complete":
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
                sms_client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
                message = sms_client.messages.create(
                    body=body,
                    from_='+13203563490',
                    to=str(client.phone_number)
                )
                print(message.sid)
            else:
                print(body)
        except Exception as e:
            print(e)


@login_required
def sendSMS(context, order_id):
    order = get_object_or_404(Order, id=order_id)
    twilioSendSMS(order, order.status)
    return redirect('detail-service-order', order_id)
