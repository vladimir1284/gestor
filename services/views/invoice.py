import tempfile
from django.http import HttpResponse
from gestor import settings
from django.shortcuts import (
    render,
)
from .order import getOrderContext
from django.contrib.auth.decorators import login_required
from services.models import (
    Payment,
)
from services.forms import (
    SendMailForm,
)
from users.forms import (
    UserProfile,
)
from utils.send_mail import MailSender
from django.utils.translation import gettext_lazy as _
from .email import sendMail, generate_invoice_pdf

# -------------------- Invoice ----------------------------


def get_invoice_context(order_id):
    context = getOrderContext(order_id)
    # Filter special services
    context['services'] = [trans for trans in context['services']
                           if not (trans.service.marketing or trans.service.internal)]
    return context


@login_required
def view_invoice(request, id):
    context = get_invoice_context(id)

    mail_address = ""
    if context['order'].associated and context['order'].associated.email:
        mail_address = context['order'].associated.email
    elif context['order'].company and context['order'].company.email:
        mail_address = context['order'].company.email

    form = SendMailForm(request.POST or None,
                        initial={'mail_address': mail_address})
    context.setdefault('form', form)
    if form.is_valid():
        sendMail(
            context, request, form.cleaned_data['mail_address'], form.cleaned_data['send_copy'])
    # Payments
    context.setdefault(
        'payments', Payment.objects.filter(order=context['order']))

    return render(request, 'services/invoice_view.html', context)


@login_required
def html_invoice(request, id):
    context = get_invoice_context(id)
    return render(request, 'services/invoice_pdf.html', context)


def generate_invoice(request, id):
    context = get_invoice_context(id)
    result = generate_invoice_pdf(context, request)

    if result is not None:
        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=invoice_towit.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response
    return None

# -------------------- Mail ----------------------------
