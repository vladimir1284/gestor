# En tu archivo views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import TwilioCall
import json

@csrf_exempt
def handle_incoming_call(request):
    print("fsjdf")
    if request.method == 'POST':
        # Convertir los datos recibidos desde Twilio a un diccionario Python
        data = request.POST
        print(request)

        # Crear una instancia del modelo TwilioCall y guardar los datos
        twilio_call = TwilioCall(
            called=data['Called'],
            to_state=data['ToState'],
            caller_country=data['CallerCountry'],
            direction=data['Direction'],
            caller_state=data['CallerState'],
            to_zip=data['ToZip'],
            call_sid=data['CallSid'],
            to_phone_number=data['To'],
            caller_zip=data['CallerZip'],
            to_country=data['ToCountry'],
            call_token=data['CallToken'],
            called_zip=data['CalledZip'],
            api_version=data['ApiVersion'],
            called_city=data['CalledCity'],
            call_status=data['CallStatus'],
            from_phone_number=data['From'],
            account_sid=data['AccountSid'],
            called_country=data['CalledCountry'],
            caller_city=data['CallerCity'],
            to_city=data['ToCity'],
            from_country=data['FromCountry'],
            caller_phone_number=data['Caller'],
            from_city=data['FromCity'],
            called_state=data['CalledState'],
            from_zip=data['FromZip'],
            from_state=data['FromState']
        )
        twilio_call.save()

        # Respondemos con un código de estado 200 OK
        return HttpResponse(status=200)
    else:
        # Si la solicitud no es de tipo POST, respondemos con un código de estado 405 Method Not Allowed
        return HttpResponse(status=405)
