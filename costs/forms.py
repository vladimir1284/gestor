from .models import Cost, CostCategory

from utils.forms import CategoryCreateForm as BaseCategoryCreateForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText
from django.utils.translation import gettext_lazy as _


class CategoryCreateForm(BaseCategoryCreateForm):

    class Meta:
        model = CostCategory
        fields = ('name', 'icon',)
