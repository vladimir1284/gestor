import jwt
from django.conf import settings
from django.shortcuts import HttpResponse
from django.shortcuts import render

from rent.tools.deposit import trailer_deposit_conditions_pdf
from rent.tools.deposit import trailer_deposit_context


def trailer_deposit_conditions(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        id = info["deposit_id"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)

    context = trailer_deposit_context(request, id)
    return render(request, "rent/trailer_deposit_conditions.html", context)


def trailer_deposit_pdf(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        id = info["deposit_id"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_inf.html", context)

    result = trailer_deposit_conditions_pdf(request, id)
    if result is not None:
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        response.status_code = 200
        response.write(result)
        return response
    return None
