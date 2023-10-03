from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from rent.models.lease import Lease, Due
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
import tempfile
from django.template.loader import render_to_string


def get_invoice_context(lease_id, date, paid):
    lease = get_object_or_404(Lease, id=lease_id)
    date = datetime.strptime(date, "%m%d%Y")
    due = Due.objects.filter(lease=lease, due_date=date).last()
    context = {'date': date,
               'lease': lease,
               'due': due,
               'paid': (paid == "true")}
    return context


@login_required
def invoice(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    return render(request, "rent/invoice/invoice_view.html", context=context)


def generate_invoice(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    result = generate_invoice_pdf(request, lease_id, date, paid)

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


def generate_invoice_pdf(request, lease_id, date, paid):
    context = get_invoice_context(lease_id, date, paid)
    """Generate pdf."""
    image = settings.STATIC_ROOT+'/assets/img/icons/TOWIT.png'
    # Render
    context.setdefault('image', image)
    html_string = render_to_string('rent/invoice/invoice_pdf.html', context)
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        main_doc = html.render(presentational_hints=True)
        return main_doc.write_pdf()
    return None
