from django.http import HttpRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from rbac.decorators.ignore import rbac_ignore


@rbac_ignore
@csrf_exempt
def whatsapp_bot(request: HttpRequest):
    if request.method != "POST":
        resp = MessagingResponse()
        msg = resp.message()
        msg.body("Hello")
        msg.media("https://towithouston.com/assets/img/logo.png")

        return HttpResponse(str(resp))

    print(request.POST)
    body = request.POST.get("Body")
    print(body)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Hello, this chatbot is under development.")
    msg.media("https://towithouston.com/assets/img/logo.png")

    return HttpResponse(str(resp))
