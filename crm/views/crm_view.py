from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from ..forms import FlaggedCallsForm, AssociatedCreateFormCrm
from users.views import *
from django.utils.translation import gettext_lazy as _
from ..models.twilio_model import Associated, TwilioCall
from ..models.crm_model import FlaggedCalls

@csrf_exempt
def flagged_call_view(request, id):
    register_row = get_object_or_404(TwilioCall, id=id)
    phone_number = register_row.from_phone_number
    initial = {"phone_number": phone_number}
    if request.method == 'POST':
        form = FlaggedCallsForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            return redirect('registro-llamadas')
    else:
        form = FlaggedCallsForm(initial=initial)

    return render(request, 'crm/borrar_del_registro.html', {'form': form})

@login_required
def create_associated(request, id):
    type = "client"
    initial = {"type": type}
    register_row = get_object_or_404(TwilioCall, id=id)
    phone_number = register_row.from_phone_number
    initial["phone_number"] = phone_number
    form = AssociatedCreateFormCrm(initial=initial)
    next = request.GET.get("next", "registro-llamadas")
    print(next)
    if request.method == "POST":
        print(1)
        form = AssociatedCreateFormCrm(request.POST, request.FILES, initial=initial)
        print(2)
        if form.is_valid():
            print(3)
            from_last_8 = phone_number[-8:]
            twilio_call_num = TwilioCall.objects.filter(from_phone_number__endswith=from_last_8)
            if not twilio_call_num.exists():
            # Maneja el caso donde no hay coincidencias
                return render(request, "users/contact_create.html", {"form": form, "title": _("No matching TwilioCall found")})
            associated: Associated = form.save()
            print(4)
            request.session["associated_id"] = associated.id
            for twilio_calls in twilio_call_num:
                twilio_calls.associated = associated  # Asignar la instancia en lugar del ID
                twilio_calls.save()  # Guardar cada instancia de TwilioCall
                print(6)

            if associated.outsource:
                print(7)
                order_id = request.session.get("order_detail")
                return redirect("create-expense", order_id)
            print(next)
            return redirect(next)
    title = {"client": _("Create client"), "provider": _("Create Provider")}[type]
    context = {"form": form, "title": title}
    addStateCity(context)
    return render(request, "users/contact_create.html", context)
