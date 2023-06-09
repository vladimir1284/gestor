from django.urls import reverse_lazy
from django.views.generic.edit import (
    UpdateView,
    CreateView,
)
from django.shortcuts import (
    redirect,
    get_object_or_404,
)
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from services.models import (
    ServiceCategory,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from services.forms import (
    CategoryCreateForm,
)
from django.utils.translation import gettext_lazy as _

# -------------------- Category ----------------------------


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = CategoryCreateForm
    template_name = 'utils/category_create.html'
    success_url = reverse_lazy('list-service-category')


class CategoryListView(LoginRequiredMixin, ListView):
    model = ServiceCategory
    template_name = 'services/category_list.html'


@login_required
def delete_category(request, id):
    # fetch the object related to passed id
    category = get_object_or_404(ServiceCategory, id=id)
    category.delete()
    return redirect('list-service-category')
