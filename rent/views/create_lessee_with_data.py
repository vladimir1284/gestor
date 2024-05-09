import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.timezone import datetime
from django.utils.timezone import timedelta
from django.utils.timezone import timezone

from rent.forms.lease import AssociatedCreateForm
from rent.forms.lease import LesseeDataForm
from rent.models.lease import Associated
from rent.models.lease import LesseeData
from users.views import addStateCity

# Client and its data


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
        "form": formLessee,
        "formLesseeData": formLesseeData,
    }
    addStateCity(context)

    return render(
        request, "rent/contract/contract_lesseedata_associated_edit.html", context
    )


# Client first and its data faster


@login_required
@atomic
def create_lessee(request, next, args: list):
    if request.method == "POST":
        form = AssociatedCreateForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            lessee = form.save()

            exp = datetime.now(timezone.utc) + timedelta(days=1)
            tokCtx = {
                "exp": exp,
                "lessee": lessee.id,
                "next": next,
                "args": args,
                "create": True,
            }
            token = jwt.encode(tokCtx, settings.SECRET_KEY, algorithm="HS256")

            return redirect("lessee_data_form", token)
    else:
        form = AssociatedCreateForm()

    title = "Create client"
    context = {
        "title": title,
        "form": form,
    }
    addStateCity(context)

    return render(request, "users/contact_create.html", context)


@login_required
@atomic
def update_lessee(request, lessee_id, next, args):
    lessee: Associated = get_object_or_404(Associated, id=lessee_id)

    if request.method == "POST":
        form = AssociatedCreateForm(
            request.POST,
            request.FILES,
            instance=lessee,
        )
        if form.is_valid():
            form.save()

            exp = datetime.now(timezone.utc) + timedelta(days=1)
            tokCtx = {
                "exp": exp,
                "lessee": lessee.id,
                "next": next,
                "args": args,
                "create": False,
            }
            token = jwt.encode(tokCtx, settings.SECRET_KEY, algorithm="HS256")

            return redirect("lessee_data_form", token)
    else:
        form = AssociatedCreateForm(instance=lessee)

    title = "Update client"
    context = {
        "title": title,
        "form": form,
    }
    addStateCity(context)

    return render(request, "users/contact_create.html", context)


# Client's data


@login_required
@atomic
def create_update_lessee_data(request, token: str):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        lessee_id = info["lessee"]
        next = info["next"]
        args = info["args"]
        create = info["create"]
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

    lessee: Associated = get_object_or_404(Associated, id=lessee_id)
    lessee_data, _ = LesseeData.objects.get_or_create(associated=lessee)

    if request.method == "POST":
        form = LesseeDataForm(
            request.POST or None,
            request.FILES or None,
            instance=lessee_data,
        )
        if form.is_valid():
            data = form.save(commit=False)
            data.associated = lessee
            data.save()

            try:
                idx = args.index("{lessee_id}")
                if idx != -1:
                    args[idx] = lessee.id
            except Exception:
                pass
            return redirect(next, *args)
    else:
        form = LesseeDataForm(instance=lessee_data)

    title = "Lessee Data"
    context = {
        "title": title,
        "form": form,
    }

    return render(request, "users/contact_create.html", context)
