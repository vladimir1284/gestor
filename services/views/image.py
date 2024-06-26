from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.forms import (
    ServicePictureForm,
)
from services.models import Order
from services.models import ServicePicture

# -------------------- Service Images -------------------------


@login_required
def create_service_pictures(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    form = ServicePictureForm(id=order_id)
    if request.method == "POST":
        form = ServicePictureForm(request.POST, request.FILES, id=order_id)
        if form.is_valid():
            image = form.save(commit=False)
            image.order = order
            image.save()
            return redirect("detail-service-order", order_id)

    # add form dictionary to context
    context = {"form": form, "order": order}

    return render(request, "services/service_image_create.html", context)


def share_service_pictures(request, ids):
    pks = list(map(int, ids.split(",")[:-1]))
    images = ServicePicture.objects.filter(pk__in=pks)
    return render(
        request,
        "services/service_images.html",
        {"images": images, "order": images[0].order},
    )


@login_required
def delete_service_picture(request, ids):
    pks = list(map(int, ids.split(",")[:-1]))
    images = ServicePicture.objects.filter(pk__in=pks)
    for img in images:
        img.delete()
    return redirect("detail-service-order", images[0].order.id)
