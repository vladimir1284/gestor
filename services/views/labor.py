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
    Service,
)
from services.forms import (
    SendMailForm,
)
from users.forms import (
    UserProfile,
)
from utils.send_mail import MailSender
from django.utils.translation import gettext_lazy as _

# -------------------- Labor ----------------------------


def get_labor_context(order_id):
    context = getOrderContext(order_id)
    # Internal services
    internal_services = Service.objects.filter(internal=True)
    context.setdefault('internal_services', internal_services)
    # Marketing services
    marketing_services = Service.objects.filter(marketing=True)
    context.setdefault('marketing_services', marketing_services)
    # Filter special services
    for trans in context['services']:
        if trans.service.tire:
            context.setdefault('tire', True)

    return context


@login_required
def view_labor(request, id):
    context = get_labor_context(id)
    # Payments
    context.setdefault(
        'payments', Payment.objects.filter(order=context['order']))
    # Workers
    context.setdefault(
        'workers', UserProfile.objects.filter(role=2))

    return render(request, 'services/labor_view.html', context)


@login_required
def html_labor(request, id):
    context = get_labor_context(id)
    return render(request, 'services/labor_pdf.html', context)


def generate_labor_pdf(context, request):
    """Generate pdf."""
    image = settings.STATIC_ROOT+'/assets/img/icons/TOWIT.png'
    # Render
    context.setdefault('image', image)
    # Workers
    context.setdefault(
        'workers', UserProfile.objects.filter(role=2))
    html_string = render_to_string('services/labor_pdf.html', context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        main_doc = html.render(presentational_hints=True)
        return main_doc.write_pdf()
    return None


def generate_labor(request, id):
    context = get_labor_context(id)
    result = generate_labor_pdf(context, request)

    if result is not None:
        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=labor_towit.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response
    return None
