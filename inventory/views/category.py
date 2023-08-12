from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView
from django.shortcuts import (
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required

from inventory.models import (
    ProductCategory,
)
from inventory.forms import (
    CategoryCreateForm,
)
from django.utils.translation import gettext_lazy as _


# -------------------- Category ----------------------------

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = 'utils/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(ProductCategory, id=id)
    category.delete()
    return redirect('list-category')
