from .models import Cost, CostCategory
from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.contrib.auth.decorators import login_required
from .forms import CategoryCreateForm


# -------------------- Category ----------------------------

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = CostCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-costs-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = CostCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-costs-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = CostCategory
    template_name = 'costs/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(CostCategory, id=id)
    category.delete()
    return redirect('list-costs-category')
