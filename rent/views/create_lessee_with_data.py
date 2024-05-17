import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import datetime
from django.utils.timezone import timedelta
from django.utils.timezone import timezone

from rent.forms.guarantor import GuarantorForm
from rent.forms.lease import AssociatedCreateForm
from rent.forms.lease import LesseeDataForm
from rent.models.lease import Associated
from rent.models.lease import LesseeData
from rent.views.lease.contract_signing import HttpRequest
from users.views import addStateCity

# Client and its data


@login_required
@atomic
def create_lessee_with_data(
    request,
    next,
    args: list,
    use_client_url: dict | None = None,
):
    if request.method == "POST":
        formLessee = AssociatedCreateForm(
            request.POST,
            request.FILES,
            use_client_url=use_client_url,
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


def save_lessee(
    request: HttpRequest,
    form: AssociatedCreateForm,
    formGuarantor: GuarantorForm,
    next: str,
    args: list,
    update_data: bool = True,
):
    if form.is_valid():
        guarantor = form.cleaned_data["has_guarantor"]
        if guarantor:
            if not formGuarantor.is_valid():
                return None
            guarantor = formGuarantor.save()
            request.session["guarantor"] = guarantor.id
            try:
                idx = args.index("{guarantor_id}")
                if idx != -1:
                    args[idx] = guarantor.id
            except Exception:
                pass

        lessee = form.save()

        if not update_data:
            try:
                idx = args.index("{lessee_id}")
                if idx != -1:
                    args[idx] = lessee.id
            except Exception:
                pass

            return redirect(next, *args)

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

    return None


@login_required
@atomic
def create_lessee(
    request,
    next,
    args: list,
    use_client_url: dict | None = None,
    update_data: bool = True,
    ask_guarantor: bool = False,
):
    request.session["guarantor"] = None
    if request.method == "POST":
        form = AssociatedCreateForm(
            request.POST,
            request.FILES,
            use_client_url=use_client_url,
            ask_guarantor=ask_guarantor,
        )
        formGuarantor = GuarantorForm(data=request.POST)
        ret = save_lessee(
            request,
            form,
            formGuarantor,
            next,
            args,
            update_data,
        )
        if ret is not None:
            return ret
    else:
        form = AssociatedCreateForm(
            use_client_url=use_client_url,
            ask_guarantor=ask_guarantor,
        )
        formGuarantor = GuarantorForm()

    title = "Create client"
    context = {
        "title": title,
        "form": form,
    }
    if ask_guarantor:
        context["formGuarantor"] = formGuarantor
    addStateCity(context)

    return render(request, "users/contact_create.html", context)


@login_required
@atomic
def update_lessee(
    request,
    lessee_id,
    next,
    args,
    update_data: bool = True,
    ask_guarantor: bool = False,
):
    request.session["guarantor"] = None
    lessee: Associated = get_object_or_404(Associated, id=lessee_id)

    if request.method == "POST":
        form = AssociatedCreateForm(
            request.POST,
            request.FILES,
            instance=lessee,
            ask_guarantor=ask_guarantor,
        )
        formGuarantor = GuarantorForm(data=request.POST)
        ret = save_lessee(
            request,
            form,
            formGuarantor,
            next,
            args,
            update_data,
        )
        if ret is not None:
            return ret
    else:
        form = AssociatedCreateForm(
            instance=lessee,
            ask_guarantor=ask_guarantor,
        )
        formGuarantor = GuarantorForm()

    title = "Update client"
    context = {
        "title": title,
        "form": form,
    }
    if ask_guarantor:
        context["formGuarantor"] = formGuarantor
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
