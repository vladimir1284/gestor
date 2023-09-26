from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
import pytz
from django.conf import settings
from datetime import datetime
from .models import Plate
from .forms import PlateForm


@login_required
def list_plate(request):
    plates = Plate.objects.filter(outgoing_date__isnull=True)
    return render(request, 'utils/list_plate.html', {'plates': plates})


@login_required
def checkout_plate(request, plate_id):
    plate = get_object_or_404(Plate, id=plate_id)
    plate.outgoing_date = datetime.now().replace(tzinfo=pytz.timezone(
        settings.TIME_ZONE))
    plate.save()
    return redirect('plate-list')


@login_required
def create_plate(request):
    if request.method == 'POST':
        form = PlateForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the list view
            return redirect('plate-list')
    else:
        form = PlateForm()

    return render(request, 'utils/plate_create.html', {'form': form})


@login_required
def detail_plate(request, plate_id):
    plate = get_object_or_404(Plate, id=plate_id)

    if request.method == 'POST':
        form = PlateForm(request.POST, instance=plate)
        if form.is_valid():
            form.save()
            # Redirect to the list view
            return redirect('plate-list')
    else:
        form = PlateForm(instance=plate)

    return render(request, 'utils/plate_create.html', {'form': form})
