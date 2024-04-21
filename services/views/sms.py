from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from services.models import Order
from services.tools.sms import *


@login_required
def sendSMS(context, order_id):
    order = get_object_or_404(Order, id=order_id)
    twilioSendSMS(order, order.status)
    return redirect("detail-service-order", order_id)
