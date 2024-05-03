import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rent.models.lease import Contract
from rent.tools.contract_ctx import get_contract_token
from rent.tools.contract_ctx import prepare_contract_view
from rent.tools.get_conditions import get_conditions
from rent.views.calendar import login_required
from rent.views.lease.update_data_on_contract import HttpRequest


@login_required
def contract_signing_id(request: HttpRequest, id: int):
    token = get_contract_token(id)
    return redirect("contract-signature", token)


def contract_signing(request, token):
    if request.method == "POST":
        return redirect(settings.REDIR_CLIENTS)

    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        contract_id = info["contract"]
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

    contract = get_object_or_404(Contract, pk=contract_id)
    # Cannot edit active contract
    if contract.stage == "active":
        return redirect("https://towithouston.com/")
    context = prepare_contract_view(contract_id)
    context.setdefault("external", True)

    context["token"] = token
    context["conditions"] = get_conditions(context)

    return render(request, "rent/contract/contract_signing.html", context)
