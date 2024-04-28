from crispy_forms.bootstrap import AppendedText
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Div
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import SafeString
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from services.models import Expense
from services.models import Payment
from services.models import PaymentCategory
from services.models import PendingPayment
from services.models import Service
from services.models import ServiceCategory
from services.models import ServicePicture
from services.models import ServiceTransaction
from services.models.order_signature import OrderSignature
from services.tools.available_positions import get_available_positions
from services.tools.get_order_dec_reazons import get_order_dec_reazons
from services.tools.storage_reazon import getStorageReazons
from utils.forms import BaseForm
from utils.forms import CategoryCreateForm as BaseCategoryCreateForm
from utils.models import Order
from utils.models import OrderDeclineReazon


class OrderCreateForm(BaseForm):
    getPlate = False

    class Meta:
        model = Order
        fields = (
            "concept",
            "note",
            "position",
            "storage_reason",
            "quotation",
            "parts_sale",
            "vin",
            "plate",
            "invoice_data",
        )

    def __init__(self, *args, get_plate=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.getPlate = get_plate

        position = kwargs["instance"].position if "instance" in kwargs.keys() else None

        availables_positions = get_available_positions(
            current_pos=position,
            unselected=True,
        )

        self.fields["position"].widget = forms.Select(choices=availables_positions)

        self.fields["invoice_data"].widget.attrs[
            "placeholder"
        ] = "Datos adicionales para mostrar en la factura"
        self.fields["note"].widget.attrs[
            "placeholder"
        ] = "Información adicional relativa a esta orden"

        if self.getPlate:
            self.helper.layout = Layout(
                Div(Div(Field("quotation")), css_class="mb-3"),
                Div(Div(Field("parts_sale")), css_class="mb-3"),
                Div(Div(Field("concept")), css_class="mb-3"),
                Div(Div(Field("vin")), css_class="mb-3"),
                Div(Div(Field("plate")), css_class="mb-3"),
                Div(Div(Field("position")), css_class="mb-3"),
                Div(Div(Field("storage_reason")), css_class="mb-3"),
                Div(Div(Field("invoice_data", rows="2")), css_class="mb-3"),
                Div(Div(Field("note", rows="2")), css_class="mb-3"),
                ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
            )
        else:
            self.helper.layout = Layout(
                Div(Div(Field("quotation")), css_class="mb-3"),
                Div(Div(Field("concept")), css_class="mb-3"),
                Div(Div(Field("vin")), css_class="mb-3"),
                Div(Div(Field("position")), css_class="mb-3"),
                Div(Div(Field("storage_reason")), css_class="mb-3"),
                Div(Div(Field("invoice_data", rows="2")), css_class="mb-3"),
                Div(Div(Field("note", rows="2")), css_class="mb-3"),
                ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
            )

    def clean_position(self):
        valor = self.cleaned_data.get("position")
        if valor == -10:
            raise forms.ValidationError("Please, select a position")
        return valor

    def clean(self):
        cleaned_data = super().clean()

        vin = cleaned_data.get("vin")
        plate = cleaned_data.get("plate")
        # pos = cleaned_data.get("position")
        #
        # if pos == "-":
        #     self.add_error("position", "Please select a position")

        if (
            self.getPlate
            and (vin is None or vin == "")
            and (plate is None or plate == "")
        ):
            self.add_error("vin", "One of VIN or Plate is required")
            self.add_error("plate", "One of VIN or Plate is required")
            # raise ValidationError("Vin or Plate is required.")


class CategoryCreateForm(BaseCategoryCreateForm):
    class Meta:
        model = ServiceCategory
        fields = (
            "name",
            "icon",
        )


class PendingPaymentCreateForm(BaseForm):
    class Meta:
        model = PendingPayment
        fields = ("amount",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(Div(Div(PrependedText("amount", "$"))))


class PaymentCreateForm(BaseForm):
    weeks = forms.IntegerField(required=False, initial=0)  # Add the "weeks" field

    class Meta:
        model = Payment
        fields = ("amount",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = self.initial["category"]
        self.fields["amount"].label = self.category.name
        if self.category.extra_charge > 0:
            self.fields["amount"].help_text = (
                f"Extra charge: {self.category.extra_charge}%"
            )

        self.helper.layout = Layout(
            Div(
                Div(PrependedText("amount", "$")),
                Div(
                    "weeks",  # Add the "weeks" field to the layout
                    # Hide the field based on condition
                    css_class="d-none" if self.category.name != "debt" else "",
                ),
            )
        )


class PaymentCategoryCreateForm(BaseForm):
    class Meta:
        model = PaymentCategory
        fields = ("name", "icon", "extra_charge")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(Div(Field("name")), css_class="mb-3"),
            Div(Div(AppendedText("extra_charge", "%")), css_class="mb-3"),
            HTML(
                """
                <img id="preview"
                {% if form.icon.value %}
                    class="img-responsive"
                    src="/media/{{ form.icon.value }}"
                {% endif %}">
                """
            ),
            Div(Div(Field("icon", css_class="form-select")), css_class="mb-3"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class CommonTransactionLayout(Layout):
    def __init__(self, *args, **kwargs):
        super().__init__(
            Div(
                Div(Field(PrependedText("price", "$")), css_class="col-md-4 mb-3"),
                Div(Div(AppendedText("tax", "%")), css_class="col-md-4 mb-3"),
                Div(Field("quantity"), css_class="col-md-4 mb-3"),
                css_class="row",
            ),
            Div(Div(Field("note", rows="2")), css_class="mb-3"),
        )


class TransactionCreateForm(forms.ModelForm):
    class Meta:
        model = ServiceTransaction
        fields = ("price", "note", "quantity", "tax")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": "autofocus"})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.add_input(Submit("submit", "Save"))
        self.helper.layout = Layout(CommonTransactionLayout())


class TransactionProviderCreateForm(TransactionCreateForm):
    associated = forms.fields_for_model(Order)["associated"]

    class Meta:
        model = ServiceTransaction
        fields = ("price", "note", "quantity", "tax", "associated")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            CommonTransactionLayout(),
            Div(
                Div(
                    Field(
                        PrependedText(
                            "associated",
                            mark_safe('<i class="bx bx-user-circle"></i>'),
                            css_class="form-select",
                        )
                    ),
                    css_class="col-10",
                ),
                Div(
                    HTML(
                        """
                    <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                       type="button"
                       href="{% url 'create-provider' %}?next={{ request.path|urlencode }}">
                        <span class="tf-icons bx bx-plus"></span>
                    </a>
                    """
                    ),
                    css_class="col-2 position-relative",
                ),
                css_class="row mb-3",
            ),
        )


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = (
            "name",
            "description",
            "category",
            "sell_tax",
            "tire",
            "internal",
            "marketing",
            "suggested_price",
        )

    def __init__(self, *args, **kwargs):
        if "title" in kwargs:
            self.title = kwargs["title"]
            kwargs.pop("title")
        else:
            self.title = _("Create Service")

        super().__init__(*args, **kwargs)
        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": "autofocus"})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        self.title,
                        Div(Div(Field("name")), css_class="mb-3"),
                        Div(Div(Field("description", rows="2")), css_class="mb-3"),
                        Div(
                            Div(Field("category", css_class="form-select")),
                            css_class="mb-3",
                        ),
                        css_class="card-body",
                    ),
                    css_class="card mb-4",
                ),
                css_class="col-xxl",
            ),
            Div(
                Div(
                    Fieldset(
                        _("Advance configuration"),
                        Div(
                            Div(Field(PrependedText("suggested_price", "$"))),
                            css_class="mb-3",
                        ),
                        Div(
                            Div(Field(AppendedText("sell_tax", "%"))), css_class="mb-3"
                        ),
                        Div(
                            Div(Field("tire"), css_class="col-3"),
                            Div(Field("internal"), css_class="col-4"),
                            Div(Field("marketing"), css_class="col-5"),
                            css_class="row mb-3",
                        ),
                        ButtonHolder(
                            Submit("submit", "Enviar", css_class="btn btn-success")
                        ),
                        css_class="card-body",
                    ),
                    css_class="card mb-4",
                ),
                css_class="col-xxl",
            ),
        )


class DiscountForm(BaseForm):
    round_to = forms.FloatField()

    class Meta:
        model = Order
        fields = ()

    def clean_round_to(self):
        round_to = self.cleaned_data["round_to"]
        error_msg = ""

        if False:
            error_msg += (
                f"The price cannot be lower than ${self.product.min_price:.2f}."
                + average
            )
            raise ValidationError(error_msg)
        return round_to

    def __init__(self, *args, **kwargs):
        self.total = int(kwargs["total"])
        kwargs.pop("total")
        self.profit = int(kwargs["profit"])
        kwargs.pop("profit")

        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Div(
                Div(Field(PrependedText("round_to", "$")), css_class="mb-3"),
                ButtonHolder(
                    Submit(
                        "submit",
                        "Create discount",
                        css_class="btn btn-success float-end",
                    )
                ),
                css_class="row mb-3",
            )
        )

        self.fields["round_to"].help_text = f"Profit: ${self.profit}"
        self.fields["round_to"].initial = self.total


class SendMailForm(forms.Form):
    send_copy = forms.BooleanField(initial=True, required=False)
    mail_address = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Focus on form field whenever error occurred
        errorList = list(self.errors)
        for item in errorList:
            self.fields[item].widget.attrs.update({"autofocus": "autofocus"})
            break

        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't render form tag
        self.helper.disable_csrf = True  # Don't render CSRF token
        self.helper.label_class = "form-label"
        self.helper.layout = Layout(
            Div(Field("mail_address"), css_class="row mb-3"),
            Div(
                Div(Field("send_copy"), css_class="col-6"),
                Div(
                    ButtonHolder(
                        Submit(
                            "submit", "Enviar", css_class="btn btn-success float-end"
                        )
                    ),
                    css_class="col-6",
                ),
                css_class="row mb-3",
            ),
        )


class ExpenseCreateForm(BaseForm):
    class Meta:
        model = Expense
        fields = (
            "concept",
            "image",
            "description",
            "cost",
            "associated",
        )

    def __init__(self, *args, capUrl=None, imgData=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Div(
                Div(
                    Field(
                        PrependedText(
                            "associated",
                            mark_safe('<i class="bx bx-user-circle"></i>'),
                            css_class="form-select",
                        )
                    ),
                    css_class="col-10",
                ),
                Div(
                    HTML(
                        """
                                <a class="btn btn-icon btn-outline-primary position-absolute bottom-0"
                                type="button"
                                href="{% url 'select-provider' %}?next={{ request.path|urlencode }}">
                                    <span class="tf-icons bx bx-plus"></span>
                                </a>
                                """
                    ),
                    css_class="col-2 position-relative",
                ),
                css_class="row mb-3",
            ),
            Div(
                HTML(
                    """
                {% load static %}
                <a href='"""
                    + str(capUrl)
                    + """' class="btn btn-outline-primary">

                    <div class="d-flex">
                        <img id="preview"
                        alt="image"
                        class="d-block rounded"
                        height="100" width="100"
                        {% if form.instance.image %}
                            src="{{ form.instance.image.url }}"
                        {% else %}
                            src="{% static 'assets/img/icons/no_image.jpg' %}"
                        {% endif %}>

                        {%if request.session.expenseCaptureImgBase64%}
                            <img id="toPreview"
                            alt="image"
                            class="d-block rounded ms-4"
                            height="100" width="100"
                            src="{{ request.session.expenseCaptureImgBase64 }}">
                        {% endif %}
                    </div>

                    Capture
                </a>
                """
                ),
                css_class="d-flex align-items-start align-items-sm-center gap-4",
            ),
            Div(
                Div(Field("image")),
                css_class="mb-3",
            ),
            Div(Div(Field("concept")), css_class="mb-3"),
            Div(Div(Field("description", rows="2")), css_class="mb-3"),
            Div(Div(Field(PrependedText("cost", "$"))), css_class="mb-3"),
            ButtonHolder(Submit("submit", "Enviar", css_class="btn btn-success")),
        )


class ServicePictureForm(BaseForm):
    class Meta:
        model = ServicePicture
        fields = ("image",)

    def __init__(self, *args, id=None, **kwargs):
        super().__init__(*args, **kwargs)
        capUrl = (
            None
            if id is None
            else reverse(
                "capture-service-picture",
                args=[id],
            )
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML(
                    """
                {% load static %}
                <img id="preview"
                alt="image"
                class="d-block rounded"
                height="100" width="100"
                {% if form.instance.image %}
                    src="{{ form.instance.image.url }}"
                {% else %}
                    src="{% static 'assets/img/icons/no_image.jpg' %}"
                {% endif %}>
                """
                ),
                css_class="d-flex align-items-start align-items-sm-center gap-4",
            ),
            Div(
                Div(
                    Field(
                        "image"
                        if id is None
                        else AppendedText(
                            "image",
                            SafeString('<a href="' + str(capUrl) + '">Capture</a>'),
                        )
                    )
                ),
                css_class="mb-3",
            ),
            ButtonHolder(Submit("submit", "Add", css_class="btn btn-success")),
        )


class OrderVinPlateForm(forms.Form):
    VIN = forms.CharField(max_length=20, required=False)
    Plate = forms.CharField(max_length=20, required=False)

    def clean(self):
        cleaned_data = super().clean()

        vin = cleaned_data.get("VIN")
        plate = cleaned_data.get("Plate")

        if vin == "" and plate == "":
            raise ValidationError("At least one field is required.")


class OrderSignatureForm(ModelForm):
    class Meta:
        model = OrderSignature
        fields = ("img",)  # 'position', 'lease')

    img = forms.CharField(max_length=2000000)


class OrderEndUpdatePositionForm(forms.Form):
    def __init__(self, *args, order: Order, status: str = "", **kwargs):
        super().__init__(*args, **kwargs)

        if status == "":
            status = str(order.status)

        end = status in ["complete", "decline"]
        position = order.position
        if end and order.trailer is not None:
            position = order.trailer.position

        reason = order.storage_reason

        if order.quotation:
            positions = [(None, "Null")]
            position = None
            readonly = True
        else:
            # if order.trailer is not None and order.associated is None:
            #     null = False
            # else:
            #     null = True
            positions, availables = get_available_positions(
                current_pos=position,
                null=end,
                availables=True,
                just_current_pos=end,
                invert_order=end,
            )
            if (reason == "" or reason is None) and not availables:
                reason = "capacity"
            readonly = False

        if reason is None or reason == "":
            if status in ["complete", "decline"]:
                reason = "ready"
            elif status == "pendding":
                reason = "approval"
            else:
                reason = "storage_service"

        if end and reason in ["approval", "capacity"]:
            reason = "ready"

        self.fields["position"] = forms.ChoiceField(
            required=False,
            choices=[("-", "---"), *positions],
            # initial=position,
            initial=position if readonly else "-",
        )
        self.fields["position"].widget.attrs["readonly"] = readonly

        self.fields["reason"] = forms.ChoiceField(
            choices=getStorageReazons(end),
            initial=reason,
        )

    def clean_position(self):
        valor = self.cleaned_data.get("position")
        if valor == "-":
            raise forms.ValidationError("Please, select a position")
        return valor


class OrderDeclineReazonForm(forms.ModelForm):
    class Meta:
        model = OrderDeclineReazon
        fields = ["decline_reazon", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["decline_reazon"] = forms.ChoiceField(
            choices=get_order_dec_reazons(),
        )

    def clean_decline_reazon(self):
        reazon = self.cleaned_data.get("decline_reazon")
        if reazon is None:
            raise forms.ValidationError("Please, select a reazon")
        return reazon
