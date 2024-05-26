from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rent.models.lease import Contract


@login_required
def contract_notes(request: HttpRequest, contract_id):
    contract: Contract = get_object_or_404(Contract, id=contract_id)

    if request.method == "POST":
        if "content" in request.POST:
            content = request.POST["content"]
            contract.push_note(content)

    return JsonResponse(contract.grouped_notes)
