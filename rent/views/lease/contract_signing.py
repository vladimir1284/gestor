import jwt
from django.conf import settings
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rent.models.lease import Contract
from rent.tools.contract_ctx import get_contract_token
from rent.tools.contract_ctx import prepare_contract_view
from rent.tools.get_conditions import get_conditions
from rent.views.calendar import login_required


@login_required
def is_contract_cli_complete(request: HttpRequest, id: int):
    contract = Contract.objects.filter(id=id).first()
    if contract is None:
        return JsonResponse({"msg": "Can not find contract"}, status="400")
    return JsonResponse({"completed": contract.client_complete})


@login_required
def contract_signing_id(request: HttpRequest, id: int):
    token = get_contract_token(id)
    return redirect("contract-signature", token)


def contract_signing(request, token):
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

    contract: Contract = get_object_or_404(Contract, pk=contract_id)
    if request.method == "POST":
        contract.client_complete = True
        contract.save()
        return redirect(settings.REDIR_CLIENTS)

    # Cannot edit active contract
    if contract.stage == "active":
        return redirect("https://towithouston.com/")
    context = prepare_contract_view(contract_id)
    context.setdefault("external", True)

    context["token"] = token
    context["conditions"] = get_conditions(context)

    return render(request, "rent/contract/contract_signing.html", context)
