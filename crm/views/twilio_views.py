from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
from ..models.crm_model import FlaggedCalls
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
        data = request.POST

        # Check if this is a call status callback
        if "CallStatus" in data and "CallSid" in data:
            return handle_call_status_callback(data)

        try:
            # Process the initial call request
            from_phone_number = data.get("From", "")
            from_phone_last_8 = from_phone_number[-8:]
            flagged_instance = FlaggedCalls.objects.filter(phone_number__endswith=from_phone_last_8).first()
            response = VoiceResponse()

            if flagged_instance is not None:
                if flagged_instance.list_type == FlaggedCalls.BLACKLIST:
                    response.reject()
                    return HttpResponse(str(response), content_type="application/xml")

                if flagged_instance.list_type == FlaggedCalls.PERSONAL:
                    dial = Dial(record=True)
                    dial.number("+12231323123")
                    response.append(dial)
                    return HttpResponse(str(response), content_type="application/xml")

            # Create a new TwilioCall instance and save the data
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

            return HttpResponse("Good", content_type="application/xml")

        except Exception as e:
            print(f"Error handling call: {e}")
            return HttpResponse("Internal Server Error", status=500)

    return HttpResponse("Good", content_type="application/xml")

def handle_call_status_callback(data):
    try:
        call_sid = data.get("CallSid", "")
        duration = data.get("CallDuration", None)
        recording_url = data.get("RecordingUrl", "")

        # Update the TwilioCall instance with duration and recording URL
        twilio_call = TwilioCall.objects.filter(call_sid=call_sid).first()
        if twilio_call:
            twilio_call.duration = duration
            twilio_call.recording_url = recording_url
            twilio_call.save()

        return HttpResponse("OK", content_type="application/xml")

    except Exception as e:
        print(f"Error handling call status callback: {e}")
        return HttpResponse("Internal Server Error", status=500)


