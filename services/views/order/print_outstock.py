import tempfile

from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from services.tools.order import getOrderContext
from utils.models import Order


def order_print_outstock_trans(request: HttpRequest, id):
    context = getOrderContext(id)

    html_string = render_to_string(
        "services/order_detail/out_stock_printable.html",
        context,
    )
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=invoice_towit.pdf"
        response["Content-Transfer-Encoding"] = "binary"
        with tempfile.NamedTemporaryFile() as output:
            output.write(result)
            output.flush()
            output = open(output.name, "rb")
            response.write(output.read())
        return response

    return JsonResponse({"msg": "Can not render"})
