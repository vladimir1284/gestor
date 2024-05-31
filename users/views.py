from datetime import datetime
from datetime import timedelta
from typing import List

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .forms import AssociatedCreateForm
from .forms import CompanyCreateForm
from .forms import ProviderCreateForm
from .forms import UserCreateForm
from .forms import UserProfileForm
from .forms import UserUpdateForm
from .models import Associated
from .models import Company
from .models import UserProfile
from rbac.decorators.admin_required import admin_required
from rent.models.lease import Contract
from rent.models.lease import Due
from rent.models.lease import Lease
from rent.models.lease import Payment as RentPayment
from services.models import DebtStatus
from services.models import Payment
from services.models import PendingPayment
from services.views.order import computeOrderAmount
from utils.models import Order


class CustomLoginView(LoginView):
    def get_success_url(self):
        self.request.session["403"] = None
        return settings.LOGIN_REDIRECT_URL


def compute_client_debt(lease: Lease):
    interval_start = get_start_paying_date(lease)
    occurrences = (
        []
        if lease.event is None
        else lease.event.get_occurrences(interval_start, timezone.now())
    )
    unpaid_dues = []
    for occurrence in occurrences:
        paid_due = Due.objects.filter(due_date=occurrence.start.date(), lease=lease)
        if len(paid_due) == 0:
            unpaid_dues.append(occurrence)
    n_unpaid = len(unpaid_dues)
    return n_unpaid * lease.payment_amount, interval_start, unpaid_dues


def get_start_paying_date(lease: Lease):
    # Find the last due payed by the client
    last_due = Due.objects.filter(lease=lease).last()
    if last_due is not None:
        interval_start = last_due.due_date + timedelta(days=2)
    else:
        # If the client hasn't paid, then start paying on effective date
        interval_start = lease.contract.effective_date - timedelta(days=1)
    # Make it timezone aware
    interval_start = timezone.make_aware(
        datetime.combine(interval_start, datetime.min.time()),
        pytz.timezone(settings.TIME_ZONE),
    )
    return interval_start


# @permission_required("auth.user.can_add_user")
@admin_required
def create_user(request):
    form = UserProfileForm()
    userCform = UserCreateForm()
    if request.method == "POST":
        userCform = UserCreateForm(request.POST)
        if userCform.is_valid():
            form = UserProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user = userCform.save()
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                return redirect("list-user")
    context = {"form": form, "user_form": userCform}
    return render(request, "users/user_create.html", context)


@login_required
def update_user(request, id):
    # fetch the object related to passed id
    profile = get_object_or_404(UserProfile, id=id)

    if profile.avatar:
        pass

    form = UserProfileForm(instance=profile)
    userCform = UserUpdateForm(instance=profile.user)

    if request.method == "POST":
        userCform = UserUpdateForm(request.POST, instance=profile.user)
        if userCform.is_valid():
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            # save the data from the form and
            # redirect to detail_view
            if form.is_valid():
                # profile.user.save()
                # profile.save()
                form.save()
                userCform.save()
                if request.user.has_perm("auth.user.can_add_user"):
                    return redirect("list-user")
                return redirect("/")

    # add form dictionary to context
    context = {"form": form, "user_form": userCform}

    return render(request, "users/user_update.html", context)


@login_required
def create_user_profile(request, id):
    user = get_object_or_404(User, id=id)
    profile = UserProfile.objects.filter(user=user).last()
    if profile is None:
        profile = UserProfile.objects.create(user=user)
    return redirect("update-user", profile.id)


# @permission_required("auth.user.can_add_user")
@admin_required
def list_user(request):
    profiles = UserProfile.objects.exclude(user__id=request.user.id)
    print(profiles)
    return render(request, "users/user_list.html", {"profiles": profiles})


# @permission_required("auth.user.can_add_user")
@admin_required
def delete_user(request, id):
    # fetch the object related to passed id
    profile = get_object_or_404(UserProfile, id=id)
    profile.user.delete()  # Profile is deleted by cascade behavior
    return redirect("list-user")


# -------------------- Associated ----------------------------

FORMS = {"client": AssociatedCreateForm, "provider": ProviderCreateForm}


@login_required
def create_provider(request):
    return create_associated(request, "provider")


@login_required
def create_client(request):
    # if request.method == "POST":
    #     form = AssociatedCreateForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         client = form.save()
    #
    #         order_data = request.session.get("creating_order")
    #         if order_data is not None:
    #             request.session["client_id"] = client.id
    #
    #             if "next" in request.session and request.session["next"] is not None:
    #                 return redirect(request.session["next"])
    #
    #             return redirect("select-company")
    #         else:
    #             if "next" in request.GET and request.GET["next"] is not None:
    #                 return redirect(request.GET["next"])
    #             if "next" in request.session and request.session["next"] is not None:
    #                 return redirect(request.session["next"])
    #             return redirect("list-client")
    # else:
    #     order_id = request.session.get('order_detail')
    #     if order_id is not None:
    #         order = get_object_or_404(Order, id=order_id)
    #         order.associated = client
    #         order.save()
    #         return redirect('detail-service-order', id=order_id)

    return create_associated(request, "client")


def addStateCity(context):
    cities = {
        "texas": {
            "houston": "Houston",
            "dallas": "Dallas",
            "austin": "Austin",
            "san_antonio": "San Antonio",
        },
        "florida": {
            "miami": "Miami",
            "tampa": "Tampa",
            "orlando": "Orlando",
            "jacksonville": "Jacksonville",
        },
    }
    context.setdefault("cities", cities)


def create_associated(request, type):
    initial = {"type": type}
    form = FORMS[type](initial=initial)
    next = request.GET.get("next", "list-{}".format(type))
    print(next)
    if request.method == "POST":
        print(1)
        form = FORMS[type](request.POST, request.FILES, initial=initial)
        print(2)
        if form.is_valid():
            print(3)
            associated: Associated = form.save()
            print(4)
            request.session["associated_id"] = associated.id
            print(6)
            if associated.outsource:
                print(7)
                order_id = request.session.get("order_detail")
                return redirect("create-expense", order_id)
            print(next)
            return redirect(next)
    title = {"client": _("Create client"), "provider": _("Create Provider")}[type]
    print(title)
    context = {"form": form, "title": title}
    addStateCity(context)
    return render(request, "users/contact_create.html", context)


@login_required
def update_associated(request, id):
    next_url = request.GET.get("next")
    only_fields = request.GET.get("only_fields", "").split(",")

    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)

    last_order = (
        Order.objects.filter(associated=associated).order_by("-created_date").first()
    )
    if not last_order:
        associated.delete_url = "delete-associated"
    else:
        associated.last_order = last_order

    # pass the object as instance in form
    # if only_fields and type(only_fields) == list:
    form = FORMS[associated.type](instance=associated, only_fields=only_fields)
    # else:
    # form = FORMS[associated.type](instance=associated)

    if request.method == "POST":
        # pass the object as instance in form
        form = FORMS[associated.type](request.POST, request.FILES, instance=associated)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            if next_url:
                return redirect(next_url)

            if associated.type == "client":
                return redirect("list-client")
            if associated.type == "provider":
                return redirect("list-provider")

    # add form dictionary to context
    title = {"client": _("Update client"), "provider": _("Update Provider")}[
        associated.type
    ]
    context = {
        "form": form,
        "title": title,
    }
    addStateCity(context)
    return render(request, "users/contact_create.html", context)


@login_required
def list_provider(request):
    return list_associated(request, "provider")


@login_required
def list_client(request):
    return list_associated(request, "client")


@login_required
def list_deactivated_client(request):
    return list_deactivated_associated(request, "client")


def getDebtOrders(debtor):
    orders = Order.objects.filter(
        associated=debtor, type="sell", status="complete"
    ).order_by("-terminated_date")
    pending_orders = []
    debt = debtor.debt
    for order in orders:
        debt_payment = Payment.objects.filter(
            order=order, category__name="debt"
        ).first()
        if debt_payment is not None:
            # Order with pending payment
            if debt > 0:
                order.debt = debt_payment.amount
                pending_orders.append(order)
                debt -= debt_payment.amount
            else:
                break
    return pending_orders


@login_required
def list_debtor(request):
    context = get_debtor(request)
    return render(request, "users/debtor_list.html", context)


def get_debtor(request):
    debtors: List[Associated] = Associated.objects.filter(
        debt__gt=0, active=True
    ).order_by("name", "alias")
    total = 0
    debtors_list = []
    for client in debtors:
        debt_status = DebtStatus.objects.filter(client=client)[0]
        if debt_status.status == "pending":
            try:
                client.oldest_debt = getDebtOrders(client)[-1]
                total += client.debt
                debtors_list.append(client)
                client.overdue = client.oldest_debt.terminated_date < (
                    datetime.now(pytz.timezone("UTC")) - timedelta(days=14)
                )
                client.last_order = (
                    Order.objects.filter(associated=client)
                    .order_by("-created_date")
                    .first()
                )
                if debt_status.weeks > 0:
                    client.weekly_payment = debt_status.amount_due_per_week
                    client.overdue = debt_status.last_modified_date < (
                        datetime.now(pytz.timezone("UTC")).date() - timedelta(days=7)
                    )
            except Exception as err:
                print(err)

    # Sort by last debt date
    debtors_list.sort(key=lambda x: x.oldest_debt.terminated_date, reverse=True)

    return {"associates": debtors_list, "total": total}


def processOrders(orders):
    orders.total = 0
    for order in orders:
        computeOrderAmount(order)
        order.amount += order.tax
        orders.total += order.amount


@login_required
def detail_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    pending_payments = PendingPayment.objects.filter(client=associated).order_by(
        "-created_date"
    )
    orders = Order.objects.filter(associated=associated).order_by(
        "-created_date", "-id"
    )
    processOrders(orders)
    if associated.debt > 0:
        pending_orders = getDebtOrders(associated)
        for order in orders:
            try:
                index = pending_orders.index(order)
                order.debt = pending_orders[index].debt
            except ValueError:
                pass  # Order without debt

    rental_debt = 0
    for contract in Contract.objects.all().filter(lessee=associated):
        if contract.stage == "active":
            lease = Lease.objects.filter(contract=contract).first()
            if lease is None:
                lease = Lease.objects.create(
                    contract=contract,
                    payment_amount=contract.payment_amount,
                    payment_frequency=contract.payment_frequency,
                    event=None,
                )
            client_debt, last_payment, unpaid_dues = compute_client_debt(lease)
            if client_debt > 0:
                last_payment = RentPayment.objects.filter(lease=lease).last()
                if last_payment is not None:
                    client_debt -= lease.remaining
            rental_debt += client_debt

        unpaid_tolls = contract.tolldue_set.all().filter(stage="unpaid")
        for toll in unpaid_tolls:
            rental_debt += toll.amount

    context = {
        "contact": associated,
        "orders": orders,
        "type": "associated",
        "title": "Associated detail",
        "pending_payments": pending_payments,
        "rental_debt": rental_debt,
    }

    return render(request, "users/contact_detail.html", context)


def list_associated(request, type):
    associates = Associated.objects.filter(type=type, active=True).order_by(
        "name", "alias"
    )
    for associated in associates:
        associated.last_order = (
            Order.objects.filter(associated=associated)
            .order_by("-created_date")
            .first()
        )
    return render(
        request, "users/associated_list.html", {"associates": associates, "type": type}
    )


def list_deactivated_associated(request, type):
    associates = Associated.objects.filter(type=type, active=False).order_by(
        "name", "alias"
    )
    for associated in associates:
        associated.last_order = (
            Order.objects.filter(associated=associated)
            .order_by("-created_date")
            .first()
        )
    return render(
        request, "users/associated_list.html", {"associates": associates, "type": type}
    )


@login_required
def delete_associated(request, id):
    # fetch the object related to passed id
    associated = get_object_or_404(Associated, id=id)
    associated.active = False
    associated.save()
    return redirect("list-{}".format(associated.type))


# -------------------- Company ----------------------------


@login_required
def create_company(request):
    form = CompanyCreateForm()
    if request.method == "POST":
        form = CompanyCreateForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            order_data = request.session.get("creating_order")
            if order_data is not None:
                client_id = request.session.get("client_id")
                if client_id is not None:
                    client = get_object_or_404(Associated, id=client_id)
                    client.company = company
                request.session["company_id"] = company.id
                return redirect("select-equipment-type")
            else:
                order_id = request.session.get("order_detail")
                if order_id is not None:
                    order = get_object_or_404(Order, id=order_id)
                    order.company = company
                    order.save()
                    return redirect("detail-service-order", id=order_id)
            return redirect("list-company")
    context = {"form": form, "title": _("Create company")}
    addStateCity(context)
    return render(request, "users/contact_create.html", context)


@login_required
def update_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)

    if not Order.objects.filter(company=company):
        company.delete_url = "delete-company"

    # pass the object as instance in form
    form = CompanyCreateForm(
        request.POST or None, request.FILES or None, instance=company
    )

    # save the data from the form and
    # redirect to list_view
    if form.is_valid():
        form.save()
        return redirect("list-company")

    # add form dictionary to context
    context = {"form": form, "title": _("Update company")}
    addStateCity(context)
    return render(request, "users/contact_create.html", context)


@login_required
def select_company(request):
    towit, created = Company.objects.get_or_create(
        name="Towithouston", defaults={"name": "Towithouston"}
    )
    if request.method == "POST":
        company = get_object_or_404(Company, id=request.POST.get("id"))
        request.session["company_id"] = company.id
        order_data = request.session.get("creating_order")
        if order_data is not None:
            if company.id == towit.id:
                return redirect("select-trailer")
            else:
                return redirect("create-service-order")
        else:
            order_id = request.session.get("order_detail")
            if order_id is not None:
                order = get_object_or_404(Order, id=order_id)
                order.company = company
                order.save()
                return redirect("detail-service-order", id=order_id)
        next = request.GET.get("next", "list-company")
        return redirect(next)
    companies = Company.objects.filter(active=True).order_by("name", "alias")
    context = {"companies": companies, "towit": towit, "skip": True}
    order_id = request.session.get("order_detail")
    if order_id is not None:
        context["skip"] = False
    return render(request, "users/company_select.html", context)


@login_required
def list_company(request):
    request.session["creating_order"] = None
    companies = Company.objects.filter(active=True).order_by("name", "alias")
    for company in companies:
        last_order = (
            Order.objects.filter(company=company).order_by("-created_date").first()
        )
        if last_order:
            company.last_order = last_order
    return render(request, "users/company_list.html", {"companies": companies})


@login_required
def detail_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)
    orders = Order.objects.filter(company=company).order_by("-created_date", "-id")
    processOrders(orders)
    context = {
        "contact": company,
        "orders": orders,
        "type": "company",
        "title": "Company detail",
    }
    return render(request, "users/contact_detail.html", context)


@login_required
def delete_company(request, id):
    # fetch the object related to passed id
    company = get_object_or_404(Company, id=id)
    company.active = False
    company.save()
    return redirect("list-company")


def generate_vcard(
    first_name=" ",
    last_name=" ",
    work=" ",
    phone_number=" ",
    email=" ",
    street=" ",
    city=" ",
    zip_code=" ",
    country="United States",
    web=" ",
):
    vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{first_name} {last_name}\nORG:{work}\nTEL:{phone_number}\nEMAIL:{email}\nADR:;{street};{city};;{zip_code};{country}\nURL:{web}\nEND:VCARD\n"
    return vcard


@login_required
def export_contact(request, type, id):
    filename = "towit-contact-"

    if id == "-1":
        filename += "all-" + type + "s"
        if type == "client" or type == "associated":
            contacts = Associated.objects.filter(active=True, type=type)
        elif type == "company":
            contacts = Company.objects.filter(active=True)
        else:
            return HttpResponseNotFound("El recurso no fue encontrado.")
    else:
        filename += type + "-" + id
        if type == "client" or type == "associated":
            contacts = [get_object_or_404(Associated, id=id)]
        elif type == "company":
            contacts = [get_object_or_404(Company, id=id)]
        else:
            return HttpResponseNotFound("El recurso no fue encontrado.")

    vcard_data = ""
    for contact in contacts:
        name_parts = (contact.name).split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:])
        phone_number = contact.phone_number
        email = contact.email
        city = contact.city
        state = contact.state
        location = city + ", " + state
        country = "United States"

        vcard_data += generate_vcard(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            city=location,
            country=country,
        )

    response = HttpResponse(vcard_data, content_type="text/vcard")
    response["Content-Disposition"] = 'attachment; filename="' + filename + '.vcf"'

    return response
