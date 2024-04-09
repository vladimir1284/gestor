import base64
import re
import tempfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from services.forms import OrderSignatureForm
from services.models.order_signature import OrderSignature
from services.models.preorder import Preorder
from services.models.preorder_data import PreorderData


@login_required
def create_handwriting(request, id):
    preorder: Preorder = get_object_or_404(Preorder, id=id)
    if preorder.preorder_data is None:
        preorder_data = PreorderData()
        preorder_data.save()
        preorder.preorder_data = preorder_data
        preorder.save()

    signature = preorder.preorder_data.signature

    if request.method == "POST":
        form = OrderSignatureForm(
            request.POST,
            request.FILES,
            instance=signature,
        )
        if form.is_valid():
            handwriting: OrderSignature = form.save(commit=False)
            handwriting.associated = preorder.preorder_data.associated
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
            preorder.preorder_data.signature = handwriting
            preorder.preorder_data.save()
            return redirect("view-conditions", id)
    else:
        form = OrderSignatureForm(instance=signature)

    context = {
        "position": "signature",
        "form": form,
        "preorder": id,
    }
    return render(request, "services/signature.html", context)
