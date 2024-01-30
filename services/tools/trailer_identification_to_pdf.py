from services.models import Order
from django.template.loader import render_to_string
from django.conf import settings


def trailer_identification_to_pdf(request, order_id):
    order = Order.objects.get(id=order_id)
    if order is None:
        return None

    context = {
        "order": order,
        "equipment": order.trailer,
    }
    html_string = render_to_string(
        "services/trailer_identification_to_pdf.html", context
    )
    if settings.USE_WEASYPRINT:
        from weasyprint import HTML

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        return html.write_pdf()
    return None
