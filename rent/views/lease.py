from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML
import tempfile
from django.conf import settings
import re
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from ..models.lease import (
    HandWriting,
    Contract,
    Inspection,
    Tire,
    LesseeData,
)
from ..forms.lease import (
    LeaseForm,
    HandWritingForm,
    InspectionForm,
    TireFormSet,
    AssociatedCreateForm,
    LesseeDataForm,
)
from users.views import addStateCity
from ..models.vehicle import Trailer
from users.models import Associated


class HandWritingCreateView(LoginRequiredMixin, CreateView):
    model = HandWriting
    form_class = HandWritingForm
    template_name = 'rent/contract/signature.html'

    def get_initial(self):
        return {'lease': self.kwargs['lease_id'],
                'position': self.kwargs['position']}

    def form_valid(self, form):
        datauri = str(form.instance.img)
        image_data = re.sub("^data:image/png;base64,", "", datauri)
        image_data = base64.b64decode(image_data)
        with tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False,
                prefix=F"firma_") as output:
            output.write(image_data)
            output.flush()
            output = open(output.name, 'rb')
            form.instance.img.save(output.name.split('/')[-1], output, True)
        return super(HandWritingCreateView, self).form_valid(form)


def get_contract(id):
    contract = Contract.objects.get(id=id)
    contract.inspection = Inspection.objects.get(lease=contract)
    contract.contract_end_date = contract.effective_date + \
        timedelta(weeks=contract.contract_term)
    contract.lessee.data = LesseeData.objects.get(associated=contract.lessee)
    return contract


@login_required
def contract_detail(request, id):
    contract = get_contract(id)
    if (contract.stage in ('active', 'signed')):
        return redirect('contract-signed', id)
    signatures = HandWriting.objects.filter(lease=contract)
    data = {'contract': contract}
    for sign in signatures:
        data.setdefault(sign.position, sign)
    return render(request, 'rent/contract/contract_detail.html', data)


@login_required
def contract_detail_signed(request, id):
    contract = get_contract(id)
    documents = None  # LeaseDocument.objects.filter(lease=contract)
    return render(request, 'rent/contract/contract_detail_signed.html',
                  {'contract': contract,
                   'documents': documents})


@login_required
def contracts(request):
    contracts = Contract.objects.all()
    return render(request, 'rent/contract/contract_list.html', {'contracts': contracts})


# class LeaseDocumentCreateView(LoginRequiredMixin, CreateView):
#     model = LeaseDocument
#     form_class = LeaseDocumentForm
#     template_name = 'rent/contract/contract_document_create.html'

#     def get_initial(self):
#         return {'lease': self.kwargs['id']}

#     def post(self, request, * args, ** kwargs):
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():
#             cd = form.save()
#             # Change the contract stage
#             cd.lease.stage = 'signed'
#             cd.lease.save()
#             # # Send email
#             # send_contract(cd.lease,
#             #               cd.document.open(mode="rb").read(),
#             #               'signed_contract')
#             # Create calendar event
#             createEvent(form.instance.lease, cd)
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)


@login_required
def update_contract_stage(request, id, stage):
    lease = get_object_or_404(Contract, id=id)
    lease.stage = stage
    lease.save()
    if (stage in ('ready', 'signed')):
        return generate_pdf(request, lease, stage)
    else:
        return redirect('detail-contract', lease.id)


def generate_pdf(request, contract, stage):
    """Generate pdf."""
    # Rendered
    signatures = HandWriting.objects.filter(lease=contract)
    data = {'contract': contract}
    for sign in signatures:
        data.setdefault(sign.position, sign.img.url)
    templates_dic = {'ready': 'contract_pdf', 'signed': 'contract_pdf_signed'}
    html_string = render_to_string(
        'rent/contract/%s.html' % templates_dic[stage], data)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=contract_for_signature.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())
        # # Send email
        # output.seek(0)
        # send_contract(contract, output.read(), 'contract_ready_for_signature')
        # if (stage == 3):
        #     # Store file
        #     output.seek(0)
        #     cd = LeaseDocument()
        #     cd.lease = contract
        #     cd.document.save("signed_contract_%s.pdf" % id, output, True)
        #     cd.save()
        #     # # Delete handwritings
        #     # for sign in signatures:
        #     #     # os.remove(os.path.join(settings.BASE_DIR, sign.img.path))
        #     #     sign.delete()
        #     createEvent(contract, cd)

    return response


def createEvent(contract, cd):
    """
    This function creates a calendar event using the Google Calendar API. 
    It takes two parameters: "contract" and "cd" (contract document).  
    First, it retrieves the credentials for accessing the Google Calendar API 
    from a JSON key file specified in the settings. It then builds the service 
    object for interacting with the API. 

    The function creates an event object with the following properties: 
    - Summary: The title of the event, which includes the contract's termination 
        information. 
    - Location: The location associated with the contract. 
    - Description: A description of the event, including a link to the document 
        associated with the contract. 
    - Start and End: The start and end dates of the contract, specified in ISO 
        format and with the timezone set to "America/Los_Angeles". 
    - Reminders: Custom reminders set for the event, including an email reminder 
        24 hours before the event and a popup reminder 12 hours before the event. 
    Finally, the function inserts the event into the specified calendar 
        (identified by the calendarId) using the service object. 
    """
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE)
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    scoped_credentials = credentials.with_scopes(SCOPES)
    service = build("calendar", "v3", credentials=scoped_credentials)
    event = {
        'summary': 'Contract: %s termination' % contract.__str__(),
        'location': contract.location,
        'description': 'Contract finish alert. Check the details here %s.' % cd.document.url,
        'start': {
            'date': contract.contract_end_date.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'date': contract.contract_end_date.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 12 * 60},
            ],
        },
    }

    event = service.events().insert(
        calendarId='towithouston@gmail.com', body=event).execute()


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = Contract
    form_class = LeaseForm
    template_name = 'rent/contract/contract_create.html'

    def get_success_url(self):
        return reverse_lazy('detail-contract', kwargs={'id': self.object.pk})


class LeseeDataUpdateView(LoginRequiredMixin, UpdateView):
    model = LesseeData
    form_class = LesseeDataForm
    template_name = 'rent/contract/lessee_data_create.html'

    def get_success_url(self):
        contract = Contract.objects.filter(
            lessee=self.object.associated).last()
        return reverse_lazy('detail-contract', kwargs={'id': contract.id})


def lease_create_view(request, lessee_id, trailer_id):
    lessee = get_object_or_404(Associated, pk=lessee_id)
    trailer = get_object_or_404(Trailer, pk=trailer_id)

    if request.method == 'POST':
        form = LeaseForm(request.POST)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.stage = 'missing'
            lease.lessee = lessee
            lease.trailer = trailer
            lease.save()
            return redirect('create-inspection', lease_id=lease.id)
    else:
        form = LeaseForm()

    context = {
        'form': form,
        'title': _('Create new contract')
    }
    return render(request, 'rent/contract/contract_create.html', context)


@login_required
def select_lessee(request, trailer_id):
    if request.method == 'POST':
        lessee = get_object_or_404(Associated, id=request.POST.get('id'))
        return redirect('update-lessee', trailer_id, lessee.id)

    # add form dictionary to context
    associates = Associated.objects.filter(
        type='client', active=True).order_by("name", "alias")
    context = {
        'associates': associates,
        'trailer_id': trailer_id,
        'create': True,
    }
    return render(request, 'services/client_list.html', context)


@login_required
def update_lessee(request, trailer_id, lessee_id=None):
    if lessee_id is not None:
        # fetch the object related to passed id
        lessee = get_object_or_404(Associated, id=lessee_id)

        # pass the object as instance in form
        form = AssociatedCreateForm(instance=lessee)

        title = _('Update client')
    else:
        form = AssociatedCreateForm()
        title = _('Create client')

    if request.method == 'POST':
        # pass the object as instance in form
        form = AssociatedCreateForm(request.POST, request.FILES)

        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            lessee = form.save()
            return redirect('update-lessee-data', trailer_id, lessee.id)

    # add form dictionary to context

    context = {
        'form': form,
        'title': title,
    }
    addStateCity(context)
    return render(request, 'users/contact_create.html', context)


@login_required
def create_lessee_data(request, trailer_id, lessee_id):
    lessee = get_object_or_404(Associated, id=lessee_id)
    try:
        lessee_data = LesseeData.objects.get(associated__id=lessee_id)
        # pass the object as instance in form
        form = LesseeDataForm(request.POST or None, request.FILES or None,
                              instance=lessee_data)
    except ObjectDoesNotExist:
        form = LesseeDataForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            data = form.save(commit=False)
            data.associated = lessee
            data.save()
            return redirect('create-contract', lessee_id, trailer_id)

    # add form dictionary to context

    context = {
        'form': form,
        'title': 'Lessee data',
    }
    addStateCity(context)
    return render(request, 'rent/contract/lessee_data_create.html', context)

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
        Tire.objects.create(type='main',
                            position=i,
                            inspection=inspection)
    for i in range(inspection.number_of_spare_tires):
        Tire.objects.create(type='spare',
                            position=i,
                            inspection=inspection)
    return inspection


@login_required
def create_inspection(request, lease_id):
    form = InspectionForm(request.POST or None)
    if request.method == 'POST':
        lease = get_object_or_404(Contract, pk=lease_id)
        if form.is_valid():
            inspection = handle_inspection(form, lease)
            return redirect('update-tires', inspection.id)
    context = {'title': 'Trailer inspection',
               'form': form}
    return render(request, 'rent/contract/inspection_create.html', context)


@login_required
def update_inspection(request, id):
    inspection = get_object_or_404(Inspection, id=id)
    form = InspectionForm(request.POST or None,
                          instance=inspection)
    if request.method == 'POST':
        if form.is_valid():
            handle_inspection(form, inspection.lease)
            return redirect('update-tires', inspection.id)
    context = {'title': 'Update trailer inspection',
               'form': form}
    return render(request, 'rent/contract/inspection_create.html', context)


@login_required
def update_tires(request, inspection_id):
    tires = Tire.objects.filter(inspection_id=inspection_id)

    formset = TireFormSet(queryset=tires)
    context = {'formset': formset,
               'title': 'Tires condition'}

    if request.method == 'POST':
        formset = TireFormSet(request.POST, queryset=tires)
        formset.save()
        inspection = get_object_or_404(Inspection, id=inspection_id)
        return redirect('detail-contract', id=inspection.lease.id)
    return render(request, 'rent/contract/update_tires.html', context)
