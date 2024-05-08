from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from rent.forms.lease import AssociatedCreateForm
from rent.forms.lease import LesseeDataForm
from rent.models.lease import Associated
from rent.models.lease import LesseeData
from users.views import addStateCity


@login_required
@atomic
def create_lessee_with_data(request, next, args: list):
    if request.method == "POST":
        formLessee = AssociatedCreateForm(
            request.POST,
            request.FILES,
        )
        formLesseeData = LesseeDataForm(
            request.POST or None,
            request.FILES or None,
        )
        if formLessee.is_valid() and formLesseeData.is_valid():
            lessee = formLessee.save()
            data = formLessee.save(commit=False)
            data.associated = lessee
            data.save()

            try:
                idx = args.index("{lessee_id}")
                if idx != -1:
                    args[idx] = lessee.id
            except Exception as e:
                pass

            return redirect(next, *args)
    else:
        formLessee = AssociatedCreateForm()
        formLesseeData = LesseeDataForm()

    title = "Update client"
    context = {
        "title": title,
        "formAssociated": formLessee,
        "formLesseeData": formLesseeData,
    }
    addStateCity(context)

    return render(
        request,
        "rent/contract/contract_lesseedata_associated_edit.html",
        context,
    )


@login_required
@atomic
def update_lessee_with_data(request, lessee_id, next, args):
    lessee: Associated = get_object_or_404(Associated, id=lessee_id)
    lessee_data = LesseeData.objects.filter(associated=lessee).last()

    if request.method == "POST":
        formLessee = AssociatedCreateForm(
            request.POST,
            request.FILES,
            instance=lessee,
        )
        formLesseeData = LesseeDataForm(
            request.POST or None,
            request.FILES or None,
            instance=lessee_data,
        )
        if formLessee.is_valid() and formLesseeData.is_valid():
            lessee = formLessee.save()
            data = formLessee.save(commit=False)
            data.associated = lessee
            data.save()

            try:
                idx = args.index("{lessee_id}")
                if idx != -1:
                    args[idx] = lessee.id
            except Exception as e:
                pass
            return redirect(next, *args)
    else:
        formLessee = AssociatedCreateForm(instance=lessee)
        formLesseeData = LesseeDataForm(instance=lessee_data)

    title = "Update client"
    context = {
        "title": title,
        "formAssociated": formLessee,
        "formLesseeData": formLesseeData,
    }
    addStateCity(context)

    return render(
        request, "rent/contract/contract_lesseedata_associated_edit.html", context
    )
