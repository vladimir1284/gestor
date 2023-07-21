import tempfile
from django.template.loader import render_to_string
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
from utils.send_mail import MailSender
from django.utils.translation import gettext_lazy as _

# -------------------- Invoice ----------------------------


@login_required
def view_invoice(request, id):
    context = getOrderContext(id)
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
            context, form.cleaned_data['mail_address'], form.cleaned_data['send_copy'])
    # Payments
    context.setdefault(
        'payments', Payment.objects.filter(order=context['order']))

    return render(request, 'services/invoice_view.html', context)


@login_required
def html_invoice(request, id):
    context = getOrderContext(id)
    return render(request, 'services/invoice_pdf.html', context)


def generate_invoice_pdf(context, request):
    """Generate pdf."""
    image = settings.STATIC_ROOT+'/images/icons/TOWIT.png'
    # Render
    context.setdefault('image', image)
    html_string = render_to_string('services/invoice_pdf.html', context)
    if settings.ENVIRONMENT == 'production':
        from weasyprint import HTML
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        main_doc = html.render(presentational_hints=True)
        return main_doc.write_pdf()
    return None


def generate_invoice(request, id):
    context = getOrderContext(id)
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


def sendMail(context, address, send_copy=False):
    invoice = generate_invoice_pdf(context)
    sender = MailSender()
    send_to = [address]
    if send_copy:
        send_to.append('info@towithouston.com')
    sender.gmail_send_invoice(
        send_to, invoice, context['order'], context['expenses'])
