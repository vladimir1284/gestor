from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rbac.decorators.ignore import rbac_ignore
from rent.models.lease import Contract
from users.models import User


@rbac_ignore
@csrf_exempt
@login_required
def contract_notes(request: HttpRequest, contract_id):
    contract: Contract = get_object_or_404(Contract, id=contract_id)

    if request.method == "POST":
        if "content" in request.POST:
            content = request.POST["content"]
            contract.push_note(request.user, content)

    grouped_notes = contract.grouped_notes
    ret_notes = []
    for _, notes in grouped_notes.items():
        if len(notes) == 0:
            continue

        json_notes = []
        for n in notes:
            try:
                file = n.file.url
            except ValueError:
                file = None
            user: User = n.created_by
            created_by = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
            }
            json_notes.append(
                {
                    "text": n.text,
                    "file": file,
                    "document_type": n.document_type,
                    "has_reminder": n.has_reminder,
                    "reminder_date": n.reminder_date,
                    "created_at": n.created_at,
                    "created_by": created_by,
                }
            )

        ret_notes.append(
            {
                "date": notes[0].created_at,
                "notes": json_notes,
            }
        )
    return JsonResponse(ret_notes, safe=False)
