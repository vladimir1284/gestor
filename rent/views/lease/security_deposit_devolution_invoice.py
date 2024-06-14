from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from gestor.views.reports import get_object_or_404
from rent.models.deposit_discount import DepositDiscount
from rent.models.lease import SecurityDepositDevolution


@login_required
def security_deposit_devolution_invoices(
    request: HttpRequest,
    id: int,
    original: bool = False,
):
    dev: SecurityDepositDevolution = get_object_or_404(SecurityDepositDevolution, id=id)
    if dev.contract is not None:
        dis: DepositDiscount = DepositDiscount.objects.filter(
            contract=dev.contract
        ).last()
    else:
        dis = None

    ctx = {
        "devolution": dev,
        "discount": dis,
        "pdf": True,
    }
    if original == True or original == "True":
        ctx["original"] = True

    html_string = render_to_string(
        "rent/deposits/devolution_invoice.html",
        ctx,
    )
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()
        if result is not None:
            response = HttpResponse(content_type="application/pdf;")
            response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            response.status_code = 200
            response.write(result)
            return response

    return render(
        request,
        "rent/deposits/devolution_invoice.html",
        ctx,
    )
