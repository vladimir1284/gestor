import base64
import re
import tempfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.debug import HttpRequest

from services.forms import OrderSignatureForm
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder


@login_required
def create_handwriting(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)
    signature = preorder.signature

    if request.method == "POST":
        form = OrderSignatureForm(
            request.POST,
            request.FILES,
            instance=signature,
        )
        if form.is_valid():
            handwriting: OrderSignature = form.save(commit=False)
            handwriting.associated = preorder.associated
            handwriting.position = "signature_order_client"

            # Save image
            datauri = str(form.instance.img)
            image_data = re.sub("^data:image/png;base64,", "", datauri)
            image_data = base64.b64decode(image_data)
            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, prefix="firma_"
            ) as output:
                output.write(image_data)
                output.flush()
                name = output.name.split("/")[-1]
                with open(output.name, "rb") as temp_file:
                    form.instance.img.save(name, temp_file, True)

            handwriting.save()
            preorder.signature = handwriting
            preorder.save()
            return redirect("view-conditions", id)
    else:
        form = OrderSignatureForm(instance=signature)

    context = {
        "position": "signature",
        "form": form,
        "preorder": id,
    }
    return render(request, "services/signature.html", context)


@login_required
def use_old_sign(request: HttpRequest, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)

    old_sign = (
        OrderSignature.objects.filter(associated=preorder.associated).last()
        if preorder.associated is not None
        else None
    )
    preorder.signature = old_sign
    preorder.new_associated = False
    preorder.save()
    return redirect("view-conditions", id)
