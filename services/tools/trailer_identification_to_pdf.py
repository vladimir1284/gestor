from django.urls import reverse
from services.models import Order
from django.template.loader import render_to_string
from django.conf import settings
import qrcode
import qrcode.image.svg


def trailer_identification_to_pdf(request, order_id):
    order = Order.objects.get(id=order_id)
    if order is None:
        return None

    phone = None
    if order.associated and order.associated.phone_number:
        phone = str(order.associated.phone_number)
        if len(order.associated.phone_number) > 4:
            phone = phone[-4:]

    url = "http://www.towithouston.com" + reverse(
        "detail-service-order", args=[order_id]
    )
    print(url)
    factory = qrcode.image.svg.SvgPathImage
    factory.QR_PATH_STYLE["fill"] = "#455565"
    img = qrcode.make(
        url,
        image_factory=factory,
        box_size=20,
    )

    context = {
        "order": order,
        "phone": phone,
        "qr_url": img.to_string(encoding="unicode"),
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
