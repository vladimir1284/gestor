from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from ..models.twilio_model import TwilioCall
from rbac.decorators.ignore import rbac_ignore
import os


@csrf_exempt
def registro(request):
    llamadas = TwilioCall.objects.all()  # Obtén todos los registros de la base de datos
    context = {
        "llamadas": llamadas,  # Pasar los registros al contexto
        "title": "Registro de Llamadas",
        "type": "client",  # o 'provider', dependiendo de tu lógica
    }
    return render(request, "crm/registro_llamadas.html", context)


""" @rbac_ignore
@csrf_exempt
def make_call(request):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    try:
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to="+13058336104",
            from_="+13203563490",
        )
        return HttpResponse(f"Call initiated with SID: {call.sid}")
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500) """


@rbac_ignore
@csrf_exempt
def handle_call(request):
    if request.method == "POST":
        # Convertir los datos recibidos desde Twilio a un diccionario Python
        data = request.POST

        # Crear una instancia del modelo TwilioCall y guardar los datos
        twilio_call = TwilioCall(
            to_state=data.get("ToState", ""),
            caller_country=data.get("CallerCountry", ""),
            direction=data.get("Direction", ""),
            caller_state=data.get("CallerState", ""),
            call_sid=data.get("CallSid", ""),
            to_phone_number=data.get("To", ""),
            to_country=data.get("ToCountry", ""),
            call_token=data.get("CallToken", ""),
            called_city=data.get("CalledCity", ""),
            call_status=data.get("CallStatus", ""),
            from_phone_number=data.get("From", ""),
            account_sid=data.get("AccountSid", ""),
            called_country=data.get("CalledCountry", ""),
            caller_city=data.get("CallerCity", ""),
            to_city=data.get("ToCity", ""),
            from_country=data.get("FromCountry", ""),
            caller_phone_number=data.get("Caller", ""),
            from_city=data.get("FromCity", ""),
            called_state=data.get("CalledState", ""),
            from_state=data.get("FromState", ""),
        )
        twilio_call.save()

    """  # Redirige la llamada al número deseado
        response = VoiceResponse()
        response.dial("+13058336104")

        return HttpResponse(str(response), content_type="application/xml")
    else:
        return HttpResponse("Method not allowed", status=405) """
    
    return HttpResponse("Good", content_type="application/xml")



