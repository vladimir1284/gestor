import base64
import re
import tempfile
from datetime import datetime
from datetime import timedelta

import jwt
import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from rent.forms.hand_writing import HandWritingForm
from rent.forms.lease import AssociatedCreateForm
from rent.forms.lease import ContractForm
from rent.forms.lease import DueForm
from rent.forms.lease import InspectionForm
from rent.forms.lease import LeaseDepositForm
from rent.forms.lease import LeaseDocumentForm
from rent.forms.lease import LeaseUpdateForm
from rent.forms.lease import LesseeDataForm
from rent.forms.lease import TireFormSet
from rent.forms.lessee_contact import LesseeContactForm
from rent.forms.trailer_deposit import TrailerDeposit
from rent.models.guarantor import Guarantor
from rent.models.lease import Contract
from rent.models.lease import Due
from rent.models.lease import HandWriting
from rent.models.lease import Inspection
from rent.models.lease import Lease
from rent.models.lease import LeaseDeposit
from rent.models.lease import LeaseDocument
from rent.models.lease import LesseeData
from rent.models.lease import Payment
from rent.models.lease import SecurityDepositDevolution
from rent.models.lease import Tire
from rent.models.vehicle import Trailer
from rent.permissions import staff_required
from rent.tools.contract_ctx import get_contract
from rent.tools.contract_ctx import get_contract_token
from rent.tools.contract_ctx import prepare_contract_view
from rent.tools.contract_email_sender import contract_email_send_sign_url
from rent.tools.get_conditions import contract_guarantor
from rent.tools.get_conditions import get_conditions
from rent.tools.get_missing_handwriting import check_handwriting
from rent.tools.get_missing_handwriting import DEFAULT_GUARANTOR_SIGNATURES
from rent.tools.get_missing_handwriting import DEFAULT_LESSEE_SIGNATURES
from rent.tools.get_missing_handwriting import get_missing_handwriting
from rent.tools.get_missing_handwriting import is_valid_as_next
from rent.tools.lessee_contact_sms import sendSMSLesseeContactURL
from rent.views.client import compute_client_debt
from rent.views.create_lessee_with_data import create_lessee
from rent.views.create_lessee_with_data import update_lessee as updateLessee
from users.models import Associated
from users.views import addStateCity
from whatsapp.tools.whatsapp import send_whatsapp


def create_handwriting(request, token, position, external=False):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        lease_id = info["contract"]
        is_guarantor = info.get("guarantor", False)
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

    contract = get_object_or_404(Contract, pk=lease_id)
    # Cannot edit active contract
    if contract.stage == "active":
        return redirect("https://towithouston.com/")
    if request.method == "POST":
        form = HandWritingForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete instance if exists
            existing_handwritings = HandWriting.objects.filter(
                lease=contract, position=position
            )
            for hw in existing_handwritings:
                hw.delete()

            handwriting: HandWriting = form.save(commit=False)
            handwriting.lease = contract
            handwriting.position = position

            # Save image
            datauri = str(form.instance.img)
            image_data = re.sub("^data:image/png;base64,", "", datauri)
            image_data = base64.b64decode(image_data)
            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, prefix="firma_"
            ) as output:
                output.write(image_data)
                output.flush()
                name = output.name.split("/")[-1]
                with open(output.name, "rb") as temp_file:
                    form.instance.img.save(name, temp_file, True)

            handwriting.save()

            if external:
                # Get missing hand writings
                missing_hws = get_missing_handwriting(contract)
                mhw = None

                # Get the first valid to change
                while len(missing_hws) > 0 and not is_valid_as_next(mhw, is_guarantor):
                    mhw = missing_hws.pop(0)

                # if exists capture
                print(mhw)
                if is_valid_as_next(mhw, is_guarantor):
                    return redirect(
                        "ext-capture-signature",
                        mhw,
                        token,
                    )

                return redirect("contract-signature", token)
            return redirect("detail-contract", contract.id)
    else:
        form = HandWritingForm()

    context = {
        "position": position,
        "date": position.startswith("date"),
        "contract": contract,
        "form": form,
        "token": token,
    }
    if external:
        context["back"] = reverse("contract-signature", args=[token])
    return render(request, "rent/contract/signature.html", context)


@login_required
def contract_detail(request, id):
    context = prepare_contract_view(id)

    contract: Contract = context["contract"]
    if contract.stage == "ended":
        return redirect("ended-contract-details", id)

    context["validated"] = Lease.objects.filter(contract=context["contract"]).exists()
    context["guarantor_required"] = contract_guarantor(context["contract"])
    context["handwriting_ok"] = check_handwriting(context["contract"])

    print(contract.stage)
    phone = contract.lessee.phone_number

    token_client, token_guarantor = get_contract_token(id)

    url_base = "{}://{}".format(request.scheme, request.get_host())
    url_client = url_base + reverse("contract-signature", args=[token_client])
    url_guarantor = url_base + reverse("contract-signature", args=[token_guarantor])

    context["url"] = url_client
    context["phone"] = phone
    context["token"] = token_client

    if contract.guarantor is not None:
        context["url_guarantor"] = url_guarantor
        context["phone_guarantor"] = contract.guarantor.guarantor_phone_number
        context["token_guarantor"] = token_guarantor

    if contract.stage in ["missing", "garbage"]:
        if phone is not None and phone != "":
            sendSMSLesseeContactURL(phone, url_client)
            send_whatsapp(
                str(phone),
                f"Please sing the contract in the following URL: {url_client}",
            )

        client = contract.lessee
        if client.email is not None and client.email != "":
            contract_email_send_sign_url(
                client.email,
                client.name,
                url_client,
                client.language,
            )

        guarantor = contract.guarantor
        if guarantor:
            if (
                guarantor.guarantor_phone_number is not None
                and guarantor.guarantor_phone_number != ""
            ):
                sendSMSLesseeContactURL(
                    guarantor.guarantor_phone_number,
                    url_guarantor,
                )
                send_whatsapp(
                    str(phone),
                    f"Please sing the contract in the following URL: {url_guarantor}",
                )
            if (
                guarantor.guarantor_email is not None
                and guarantor.guarantor_email != ""
            ):
                contract_email_send_sign_url(
                    guarantor.guarantor_email,
                    guarantor.guarantor_name,
                    url_guarantor,
                )

    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url_client,
        image_factory=factory,
        box_size=20,
    )
    context["qr_url"] = img.to_string(encoding="unicode")

    if contract.guarantor is not None:
        factory = qrcode.image.svg.SvgPathImage
        factory.QR_PATH_STYLE["fill"] = "#455565"
        img = qrcode.make(
            url_guarantor,
            image_factory=factory,
            box_size=20,
        )
        context["qr_url_guarantor"] = img.to_string(encoding="unicode")

    context["conditions"] = get_conditions(context)

    return render(request, "rent/contract/contract_detail.html", context)


@login_required
def contract_detail_signed(request, id):
    contract = get_contract(id)
    documents = None  # LeaseDocument.objects.filter(lease=contract)
    return render(
        request,
        "rent/contract/contract_detail_signed.html",
        {"contract": contract, "documents": documents},
    )


@login_required
def contracts(request):
    contracts = Contract.objects.all()
    return render(request, "rent/contract/contract_list.html", {"contracts": contracts})


@login_required
def create_document_on_ended_contract(request, id):
    contract = get_object_or_404(Contract, id=id)
    if request.method == "POST":
        form = LeaseDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.lease = None
            document.contract = contract
            document.save()
            messages.success(request, "Document created successfully.")
            return redirect("adjust-deposit", id=id)
    else:
        form = LeaseDocumentForm()

    context = {"form": form, "title": _("Add document")}
    return render(request, "rent/trailer_document_create.html", context)


@login_required
@staff_required
def delete_document_on_ended_contract(request, id):
    document = get_object_or_404(LeaseDocument, id=id)
    document.delete()
    messages.success(request, "Document deleted successfully.")
    return redirect("adjust-deposit", id=document.contract.id)


@login_required
@staff_required
def update_lease(request, id):
    lease = get_object_or_404(Lease, id=id)
    lease.compute_payment_cover()
    if request.method == "POST":
        form = LeaseUpdateForm(request.POST, instance=lease)
        if form.is_valid():
            form.save()
            return redirect("client-detail", lease.contract.lessee.id)
    form = LeaseUpdateForm(instance=lease)
    context = {
        "title": "Update lease terms",
        "form": form,
    }
    return render(request, "rent/contract/contract_create.html", context)


@login_required
@staff_required
@transaction.atomic
def create_due(request, lease_id, date):
    lease = get_object_or_404(Lease, id=lease_id)
    date = datetime.strptime(date, "%m%d%Y")

    if request.method == "POST":
        form = DueForm(request.POST)
        if form.is_valid():
            due: Due = form.save(commit=False)
            due.due_date = date
            due.lease = lease
            due.client = lease.contract.lessee

            # Create a payment
            Payment.objects.create(
                date_of_payment=timezone.now().date(),
                amount=due.amount,
                client=lease.contract.lessee,
                lease=lease,
                date=timezone.now(),
                user=request.user,
            )

            # Persist the due
            due.save()
            return redirect("client-detail", lease.contract.lessee.id)
    form = DueForm(initial={"amount": lease.payment_amount})
    context = {
        "title": f"Invoice for {lease.contract.lessee} on " + date.strftime("%m/%d/%Y"),
        "form": form,
        "initial": lease.payment_amount,
    }
    return render(request, "rent/client/due_create.html", context)


@login_required
@staff_required
def update_due(request, id):
    due = get_object_or_404(Due, id=id)

    if request.method == "POST":
        form = DueForm(request.POST, instance=due)
        if form.is_valid():
            form.save()
            return redirect("client-detail", due.lease.contract.lessee.id)
    form = DueForm(instance=due)
    context = {
        "title": f"Invoice for {due.lease.contract.lessee} on "
        + due.due_date.strftime("%m/%d/%Y"),
        "form": form,
    }
    return render(request, "rent/contract/contract_create.html", context)


@login_required
@staff_required
@transaction.atomic
def update_contract_stage(request, id, stage):
    contract: Contract = get_object_or_404(Contract, id=id)
    on_hold = TrailerDeposit.objects.filter(contract=contract).first()

    contract.user = request.user
    contract.stage = stage
    contract.client_complete = False
    if stage == "active":
        missing_handws = get_missing_handwriting(contract)
        if len(missing_handws) > 0:
            return redirect("detail-contract", id)
        lease = Lease.objects.create(
            contract=contract,
            payment_amount=contract.payment_amount,
            payment_frequency=contract.payment_frequency,
            event=None,
        )
        if on_hold is not None:
            LeaseDeposit.objects.create(
                lease=lease,
                date=on_hold.date,
                amount=on_hold.amount,
                note=on_hold.note,
                on_hold=True,
            )
            SecurityDepositDevolution.objects.create(
                contract=contract,
                total_deposited_amount=on_hold.amount,
            )
        mail_send_contract(request, id)
        contract.save()
        return redirect("client-detail", contract.lessee.id, contract.id)
    if stage == "ended":
        contract.ended_date = timezone.now()
        # Compute the final debt
        leases = Lease.objects.filter(contract=contract)
        lease = leases.last()
        if lease is not None:
            if contract.contract_type == "lto":
                paid, _ = contract.paid()
                contract.final_debt = contract.total_amount - paid
            else:
                contract.final_debt, _, _ = compute_client_debt(lease)
                contract.final_debt -= lease.remaining
        # Remove lease
        for lease in leases:
            lease.delete()
        contract.save()
        return redirect("ended-contract-details", contract.id)
        # return redirect("dashboard")
        # return redirect("detail-trailer", contract.trailer.id)
    contract.save()
    if stage == "garbage":
        return redirect("client-list")

    return redirect("detail-contract", id)


@login_required
def contract_pdf(request, id):
    result = generate_pdf(request, id)

    # Creating http response
    response = HttpResponse(content_type="application/pdf;")
    response["Content-Disposition"] = "inline; filename=contract_for_signature.pdf"
    response["Content-Transfer-Encoding"] = "binary"
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, "rb")
        response.write(output.read())

    return response


def mail_send_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    filename = f"contract_trailer_lease_{contract.id}"
    body = f"""Dear {contract.lessee.name},

I hope this email finds you well. We are pleased to inform you that the trailer lease contract for your recent agreement with Towit Houston has been successfully signed and executed.

As promised, we have attached a PDF copy of the fully executed contract for your reference and records.

This document contains all the pertinent details of our lease agreement, including terms, conditions, and any additional arrangements that were discussed and agreed upon. We encourage you to review it carefully to ensure that all the terms align with your expectations and requirements.

If you have any questions or require further clarification about any aspect of the contract, please do not hesitate to reach out to our team. We are here to assist you and address any concerns you may have.

Thank you for choosing Towit Houston as your trusted partner for your trailer leasing needs. We look forward to a successful and mutually beneficial business relationship.

Should you need any assistance or have any inquiries in the future, please feel free to contact us at https://towithouston.com.

Thank you for your continued trust and partnership.

Sincerely,

Daniel Hernández Duarte
LEASER
Towit Houston
tel:+1(305) 833-6104
"""
    if contract.lessee.language == "spanish":
        body = f"""Estimado {contract.lessee.name},

Espero que se encuentre bien. Nos complace informarle que el contrato de arrendamiento de remolque correspondiente a su reciente acuerdo con Towit Houston se ha firmado y ejecutado con éxito.

Como prometimos, adjuntamos una copia en PDF del contrato completamente ejecutado para su referencia y registros.

Este documento contiene todos los detalles pertinentes de nuestro contrato de arrendamiento, incluidos los términos, condiciones y cualquier acuerdo adicional que se discutió y acordó. Le recomendamos que lo revise detenidamente para asegurarse de que todos los términos se ajusten a sus expectativas y requisitos.

Si tiene alguna pregunta o necesita más aclaraciones sobre cualquier aspecto del contrato, no dude en comunicarse con nuestro equipo. Estamos aquí para ayudarle y abordar cualquier inquietud que pueda tener.

Gracias por elegir Towit Houston como su socio de confianza para sus necesidades de arrendamiento de remolques. Esperamos tener una relación comercial exitosa y mutuamente beneficiosa.

Si necesita ayuda o tiene alguna consulta en el futuro, no dude en contactarnos en https://towithouston.com.

Gracias por su continua confianza y colaboración.

Atentamente,

Daniel Hernández Duarte
ARRENDADOR
Towit Houston
teléfono:+1(305) 833-6104
"""
    try:
        if settings.ENVIRONMENT == "production":
            result = generate_pdf(request, contract_id)
            if result:
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False, prefix=filename
                ) as output:
                    output.write(result)
                    output.flush()
                    with get_connection(
                        host=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        use_tls=settings.EMAIL_USE_TLS,
                    ) as connection:
                        subject = "Signed Trailer Lease Contract - Towit Houston"
                        email_from = settings.EMAIL_HOST_USER
                        msg = EmailMessage(
                            subject,
                            body,
                            email_from,
                            (contract.lessee.email,),
                            connection=connection,
                        )
                        msg.attach_file(output.name)
                        msg.send()
        else:
            print(body)
    except Exception as e:
        print(e)


def generate_pdf(request, id):
    """Generate pdf."""
    contract = Contract.objects.get(id=id)
    # Rendered
    HandWriting.objects.filter(lease=contract)
    context = prepare_contract_view(id)
    context.setdefault("pdf", True)

    context["conditions"] = get_conditions(context)

    html_string = render_to_string("rent/contract/contract_pdf.html", context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        return html.write_pdf()
    return None


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = "rent/contract/contract_create.html"

    def get_success_url(self):
        return reverse_lazy("detail-contract", kwargs={"id": self.object.pk})


class LeseeDataUpdateView(LoginRequiredMixin, UpdateView):
    model = LesseeData
    form_class = LesseeDataForm
    template_name = "rent/contract/lessee_data_create.html"

    def get_success_url(self):
        contract = Contract.objects.filter(lessee=self.object.associated).last()
        return reverse_lazy("detail-contract", kwargs={"id": contract.id})


@staff_required
def contract_create_view(request, lessee_id, trailer_id, deposit_id=None):
    lessee = get_object_or_404(Associated, pk=lessee_id)
    trailer = get_object_or_404(Trailer, pk=trailer_id)

    # Check if there is not any other contract for this trailer...
    # Its happend when the user go back on the browser and generate various contract...
    others_contracts = Contract.objects.filter(trailer=trailer).exclude(
        stage__in=["ended", "garbage"]
    )
    if others_contracts.exists():
        print("Multiple contracts...")
        context = {
            "contracts": others_contracts,
        }
        return render(
            request, "rent/contract/contract_conflict/multiples_contracts.html", context
        )

    deposit: TrailerDeposit | None = (
        None if deposit_id is None else get_object_or_404(TrailerDeposit, pk=deposit_id)
    )

    initial = {
        "effective_date": datetime.now(),
    }

    if request.method == "POST":
        form = ContractForm(
            request.POST,
            initial=initial,
        )
        if form.is_valid():
            with transaction.atomic():
                lease: Contract = form.save(commit=False)
                lease.stage = "missing"
                lease.lessee = lessee
                lease.trailer = trailer

                if (
                    "guarantor" in request.session
                    and request.session["guarantor"] is not None
                ):
                    guarantor = Guarantor.objects.filter(
                        id=int(request.session["guarantor"])
                    ).last()
                    lease.template_version = 3
                    lease.guarantor = guarantor
                else:
                    lease.template_version = 2

                lease.save()
                if deposit is not None:
                    deposit.done = True
                    deposit.contract = lease
                    deposit.save()

                # if contract_guarantor(lease):
                #     return redirect("select-contract-guarantor", lease.id)
                return redirect("detail-contract", lease.id)
    else:
        form = ContractForm(
            initial=initial,
        )

    context = {
        "form": form,
        "title": _("Create new contract"),
        "on_hold": deposit,
    }
    return render(request, "rent/contract/contract_create.html", context)


@login_required
@staff_required
def select_lessee(request, trailer_id):
    if request.method == "POST":
        lessee = get_object_or_404(Associated, id=request.POST.get("id"))
        return redirect("update-lessee", trailer_id, lessee.id)

    # add form dictionary to context
    associates = Associated.objects.filter(type="client", active=True).order_by(
        "name", "alias"
    )
    context = {
        "associates": associates,
        "trailer_id": trailer_id,
        "create": True,
    }
    return render(request, "services/client_list.html", context)


@login_required
@staff_required
def update_lessee(request, trailer_id, lessee_id=None, deposit_id=None):
    args = ["{lessee_id}", trailer_id]
    cli_args = [trailer_id, "{client_id}"]
    if deposit_id is not None:
        args.append(deposit_id)
        cli_args.append(deposit_id)

    if lessee_id is None:
        return create_lessee(
            request,
            "create-contract",
            args,
            use_client_url={
                "url": "update-lessee",
                "args": cli_args,
            },
            ask_guarantor=True,
        )

    return updateLessee(
        request,
        lessee_id,
        "create-contract",
        args,
        ask_guarantor=True,
    )

    # if lessee_id is not None:
    #     # fetch the object related to passed id
    #     lessee = get_object_or_404(Associated, id=lessee_id)
    #
    #     if request.method == "POST":
    #         # pass the object as instance in form
    #         form = AssociatedCreateForm(request.POST, request.FILES, instance=lessee)
    #
    #         # save the data from the form and
    #         # redirect to update lessee data view
    #         if form.is_valid():
    #             form.save()
    #             if deposit_id is None:
    #                 return redirect("update-lessee-data", trailer_id, lessee.id)
    #             return redirect("update-lessee-data", trailer_id, lessee.id, deposit_id)
    #
    #     # pass the object as instance in form
    #     form = AssociatedCreateForm(instance=lessee)
    #     title = _("Update client")
    # else:
    #     if request.method == "POST":
    #         # pass the object as instance in form
    #         form = AssociatedCreateForm(request.POST, request.FILES)
    #
    #         # save the data from the form and
    #         # redirect to update lessee data view
    #         if form.is_valid():
    #             lessee = form.save()
    #             return redirect("update-lessee-data", trailer_id, lessee.id)
    #
    #     form = AssociatedCreateForm()
    #     title = _("Create client")
    #
    # # add form dictionary to context
    #
    # context = {
    #     "form": form,
    #     "title": title,
    # }
    # addStateCity(context)
    # return render(request, "users/contact_create.html", context)


@login_required
def create_lessee_contact(request, trailer_id):
    if request.method == "POST":
        form = LesseeContactForm(request.POST, request.FILES)
        if form.is_valid():
            associated = form.save()
            return redirect("generate-lessee-url", trailer_id, associated.id)
    else:
        form = LesseeContactForm()

    title = _("Create client")

    context = {
        "form": form,
        "title": title,
    }
    addStateCity(context)
    return render(request, "users/lessee_contact_create.html", context)


@login_required
@staff_required
def create_lessee_data(request, trailer_id, lessee_id, deposit_id=None):
    lessee = get_object_or_404(Associated, id=lessee_id)
    try:
        lessee_data = LesseeData.objects.get(associated__id=lessee_id)
        # pass the object as instance in form
        form = LesseeDataForm(
            request.POST or None, request.FILES or None, instance=lessee_data
        )
    except ObjectDoesNotExist:
        form = LesseeDataForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            data = form.save(commit=False)
            data.associated = lessee
            data.save()
            if deposit_id is None:
                return redirect("create-contract", lessee_id, trailer_id)
            return redirect("create-contract", lessee_id, trailer_id, deposit_id)

    # add form dictionary to context

    context = {
        "form": form,
        "title": "Lessee data",
    }
    addStateCity(context)
    return render(request, "rent/contract/lessee_data_create.html", context)


@login_required
def generate_url(request, trailer_id, associated_id):
    if request.method == "POST":
        return redirect("update-lessee", trailer_id, associated_id)

    associated = Associated.objects.get(id=associated_id)

    exp = datetime.utcnow() + timedelta(minutes=30)
    context = {
        "trailer_id": trailer_id,
        "lessee_id": associated.id,
        "name": associated.name,
        "phone": str(associated.phone_number),
        "exp": exp,
    }

    token = jwt.encode(context, settings.SECRET_KEY, algorithm="HS256")

    url_base = "{}://{}".format(request.scheme, request.get_host())
    url = url_base + reverse("lessee-form", args=[token])
    context["url"] = url

    sendSMSLesseeContactURL(associated.phone_number, url)

    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=20,
    )
    context["qr_url"] = img.to_string(encoding="unicode")

    return render(request, "rent/client/lessee_url.html", context)


def lessee_form(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        lessee_id = info["lessee_id"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)

    lessee = get_object_or_404(Associated, id=lessee_id)

    if request.method == "POST":
        form = AssociatedCreateForm(request.POST, request.FILES, instance=lessee)
        if form.is_valid():
            form.save()
            return redirect("client-create-lessee-data", token)

    form = AssociatedCreateForm(instance=lessee)
    title = _("Complete form")

    context = {
        "form": form,
        "title": title,
    }
    addStateCity(context)
    return render(request, "users/lessee_form.html", context)


def client_create_lessee_data(request, token):
    try:
        info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        lessee_id = info["lessee_id"]
    except jwt.ExpiredSignatureError:
        context = {
            "title": "Error",
            "msg": "Expirated token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)
    except jwt.InvalidTokenError:
        context = {
            "title": "Error",
            "msg": "Invalid token",
            "err": True,
        }
        return render(request, "rent/client/lessee_form_err.html", context)

    lessee = get_object_or_404(Associated, id=lessee_id)
    try:
        lessee_data = LesseeData.objects.get(associated__id=lessee_id)
        # pass the object as instance in form
        form = LesseeDataForm(
            request.POST or None, request.FILES or None, instance=lessee_data
        )
    except ObjectDoesNotExist:
        form = LesseeDataForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            data = form.save(commit=False)
            data.associated = lessee
            data.save()
            # return redirect("create-contract", lessee_id, trailer_id)
            return redirect("lessee-form-completed")

    # add form dictionary to context

    context = {
        "form": form,
        "title": "Lessee data",
    }
    addStateCity(context)
    return render(request, "users/lessee_form.html", context)
    # return render(request, "rent/contract/lessee_data_create.html", context)


def lessee_form_ok(request):
    context = {
        "title": "Form saved",
        "msg": "All data was saved",
        "err": False,
    }
    return render(request, "rent/client/lessee_form_inf.html", context)


# -------------------- Inspection ----------------------------


@transaction.atomic
def handle_inspection(form, lease):
    inspection: Inspection = form.save(commit=False)
    inspection.lease = lease
    inspection.save()
    # Delete old tires if any
    Tire.objects.filter(inspection=inspection).delete()
    # Create tires
    for i in range(inspection.number_of_main_tires):
        Tire.objects.create(type="main", position=i, inspection=inspection)
    for i in range(inspection.number_of_spare_tires):
        Tire.objects.create(type="spare", position=i, inspection=inspection)
    return inspection


@login_required
def create_inspection(request, lease_id):
    form = InspectionForm(request.POST or None)
    if request.method == "POST":
        lease = get_object_or_404(Contract, pk=lease_id)
        if form.is_valid():
            inspection = handle_inspection(form, lease)
            return redirect("update-tires", inspection.id)
    context = {"title": "Trailer inspection", "form": form}
    return render(request, "rent/contract/inspection_create.html", context)


@login_required
def update_inspection(request, id):
    inspection = get_object_or_404(Inspection, id=id)
    form = InspectionForm(request.POST or None, instance=inspection)
    if request.method == "POST":
        if form.is_valid():
            handle_inspection(form, inspection.lease)
            return redirect("update-tires", inspection.id)
    context = {"title": "Update trailer inspection", "form": form}
    return render(request, "rent/contract/inspection_create.html", context)


@login_required
def update_tires(request, inspection_id):
    tires = Tire.objects.filter(inspection_id=inspection_id)

    formset = TireFormSet(queryset=tires)
    context = {"formset": formset, "title": "Tires condition"}

    if request.method == "POST":
        formset = TireFormSet(request.POST, queryset=tires)
        formset.save()
        inspection = get_object_or_404(Inspection, id=inspection_id)
        return redirect("detail-contract", id=inspection.lease.id)
    return render(request, "rent/contract/update_tires.html", context)


# -------------------- Document ----------------------------


@login_required
def create_document(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)
    if request.method == "POST":
        form = LeaseDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.lease = lease
            document.contract = lease.contract
            document.save()
            messages.success(request, "Document created successfully.")
            return redirect("client-detail", id=lease.contract.lessee.id)
    else:
        form = LeaseDocumentForm()

    context = {"form": form, "title": _("Add document")}
    return render(request, "rent/trailer_document_create.html", context)


@login_required
@staff_required
def update_document(request, id):
    document = get_object_or_404(LeaseDocument, id=id)
    form = LeaseDocumentForm(
        request.POST or None, request.FILES or None, instance=document
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Document updated successfully.")
            return redirect("client-detail", id=document.lease.contract.lessee.id)

    context = {"form": form, "title": _("Update document")}
    return render(request, "rent/trailer_document_create.html", context)


@login_required
@staff_required
def delete_document(request, id):
    document = get_object_or_404(LeaseDocument, id=id)
    document.delete()
    messages.success(request, "Document deleted successfully.")
    return redirect("client-detail", id=document.lease.contract.lessee.id)


# -------------------- Deposit ----------------------------


@login_required
@staff_required
def create_deposit(request, lease_id):
    lease = get_object_or_404(Lease, id=lease_id)
    security_deposit, c = SecurityDepositDevolution.objects.get_or_create(
        contract=lease.contract
    )
    if request.method == "POST":
        form = LeaseDepositForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.lease = lease
            deposit.save()
            messages.success(request, "Deposit created successfully.")
            security_deposit.total_deposited_amount += deposit.amount
            security_deposit.save()
            return redirect("client-detail", id=lease.contract.lessee.id)
    else:
        form = LeaseDepositForm()

    context = {"form": form, "title": _("New Deposit")}
    return render(request, "rent/trailer_deposit_create.html", context)


@login_required
@staff_required
def delete_deposit(request, id):
    deposit = get_object_or_404(LeaseDeposit, id=id)
    security_deposit = get_object_or_404(
        SecurityDepositDevolution, contract=deposit.lease.contract
    )
    security_deposit.total_deposited_amount -= deposit.amount
    security_deposit.save()
    deposit.delete()
    messages.success(request, "Deposit deleted successfully.")
    return redirect("client-detail", id=deposit.lease.contract.lessee.id)
