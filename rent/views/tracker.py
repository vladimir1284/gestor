import pytz
from typing import List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from rent.forms.tracker import TrackerForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse
from ..models.tracker import (
    Tracker,
    TrackerUpload)
from datetime import datetime, timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from django.http import JsonResponse
import json
from requests.auth import HTTPBasicAuth

from .bat_percent import vbat2percent
from rent.permissions import staff_required


class TrackerUpdateView(LoginRequiredMixin, UpdateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'rent/tracker/tracker_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update tracker'
        return context


class TrackerCreateView(LoginRequiredMixin, CreateView):
    model = Tracker
    form_class = TrackerForm
    template_name = 'rent/tracker/tracker_create.html'

    def get_initial(self):
        try:
            trailer_id = self.kwargs['trailer_id']
        except:
            trailer_id = None
        return {'trailer': trailer_id}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create tracker'
        return context


@login_required
@staff_required
def delete_tracker(request, id):
    try:
        tracker = Tracker.objects.get(id=id)
        trailer_id = tracker.trailer.id
        tracker.delete()
        return redirect('detail-trailer', trailer_id)
    except:
        return redirect('list-trailer')


@login_required
def tracker_detail(request, id):
    tracker = Tracker.objects.get(id=id)
    data_v1 = TrackerUpload.objects.filter(
        tracker=tracker).order_by("-timestamp")
    return render(request, 'rent/tracker/tracker_data.html',
                  getTrackerUpload(id, 30))


def getTrackerUpload(id, n):
    tracker = Tracker.objects.get(id=id)
    online = False
    try:
        data = TrackerUpload.objects.filter(
            tracker=tracker).order_by("-timestamp")[:n]

        for item in data:
            # Get coordinates remotely if the data came from LTE cell
            if item.latitude is None:
                url = F"http://opencellid.org/cell/get?key={settings.OCELLID_KEY}&mcc={item.mcc}&mnc={item.mnc}&lac={item.lac}&cellid={item.cellid}&format=json"
                response = requests.get(url)
                if response.status_code == 200:
                    print("Location data downloaded for Tracker {} at {}".format(
                        tracker.id, item.timestamp))
                    json_data = response.json()
                    item.latitude = json_data['lat']
                    item.longitude = json_data['lon']
                    item.speed = 0
                    item.save()

            # Get percent of charge
            item.battery = vbat2percent(item.battery)

        if (data[0].charging):  # Powered
            max_elapsed_time = 4800
        else:
            max_elapsed_time = 80*tracker.Tint

        elapsed_time = (timezone.now() - data[0].timestamp).total_seconds()

        # print("elapsed_time: %is" % elapsed_time)
        # print("max_elapsed_time: %is" % max_elapsed_time)

        online = elapsed_time < max_elapsed_time
    except Exception as err:
        print(err)
    return {'tracker': tracker,
            'data': data[0],
            'online': online,
            'history': data}


@login_required
def trackers(request):
    trackers = Tracker.objects.all()
    return render(request, 'rent/tracker/trackers.html', {'trackers': trackers})


@login_required
def trackers_table(request):
    trackers = Tracker.objects.all()
    trackers = []
    for tracker in trackers:
        try:
            # V1.0
            data_v1 = TrackerUpload.objects.filter(
                tracker=tracker).order_by("-timestamp")
            td = data_v1[0]
            td.mode = {True: 0, False: 1}[td.charging]
            if (td.charging):  # Powered
                max_elapsed_time = 4800
            else:
                max_elapsed_time = 80*tracker.Tint

            elapsed_time = (datetime.now().replace(tzinfo=pytz.timezone(
                settings.TIME_ZONE)) - td.timestamp).total_seconds()

            print("elapsed_time: %is" % elapsed_time)
            print("max_elapsed_time: %is" % max_elapsed_time)

            online = elapsed_time < max_elapsed_time

            trackers.append({
                'id': td.tracker.id,
                'updated': td.timestamp,
                'bat': int(vbat2percent(td.battery)*100)/100.,
                'mode': td.mode,
                'online': online,
                'lessee_name': td.tracker.lessee_name,
                'trailer_description': td.tracker.trailer_description,
            })

        except Exception as err:
            print(err)
    return render(request, 'rent/tracker/trackers_table.html', {'trackers': trackers})


@csrf_exempt
def tracker_upload(request):
    # Incoming data from a tracker v1.0
    if request.method == 'POST':
        """
          Parse data from tracker
          msg structure:    
            imei,seq,mode,event,lat,lon,speed,heading,sats,vbat
        """
        try:
            msg = request.body.decode()
            print(msg)
        except:
            return HttpResponse("Wrong codification!")
        try:
            data = msg.split(',')

            imei = int(data[0])
            try:
                tracker = Tracker.objects.get(imei=imei)
                print(tracker)
            except:
                return HttpResponse("Unknown IMEI %s!" % imei)

            seq = int(data[1])
            charging = bool(int(data[2]))
            vbat = int(data[3])/1000.  # Volts
            wur = int(data[4])  # WakeUp reason
            wdgc = int(data[5])  # Watchdog resets count
            source = data[6]  # LTE or GPS
            print("IMEI #: %i" % imei)
            print("seq #: %i" % seq)
            print("Charging: %r" % charging)
            print("WakeUp reason: %i" % wur)
            print("Watchdog resets count: %i" % wdgc)
            print("vbat: %.3fV" % vbat)
            print("Datasource: %s" % source)

            if source == 'LTE':
                # 310-410,0x712A,137002000
                # mcc-mnc,lac,cellid
                mcc_mnc = data[7].split('-')
                mcc = int(mcc_mnc[0])
                mnc = int(mcc_mnc[1])
                lac = int(data[8], 16)
                cellid = int(data[9])
                print("mcc: %i" % mcc)
                print("mnc: %i" % mnc)
                print("lac: %i" % lac)
                print("Cell ID: %i" % cellid)

                td = TrackerUpload(tracker=tracker,
                                   timestamp=datetime.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                   sequence=seq,
                                   charging=charging,
                                   battery=vbat,
                                   wur=wur,
                                   wdgc=wdgc,
                                   source=source,
                                   mcc=mcc,
                                   mnc=mnc,
                                   lac=lac,
                                   cellid=cellid)

            if source == 'GPS':
                lat = float(data[7])
                lon = float(data[8])
                speed = int(data[9])
                precision = int(data[10])
                print("lat: %.5f" % lat)
                print("lon: %.5f" % lon)
                print("speed: %.2fkm/h" % speed)
                print("precision: %i" % precision)

                td = TrackerUpload(tracker=tracker,
                                   timestamp=datetime.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                   sequence=seq,
                                   charging=charging,
                                   battery=vbat,
                                   wur=wur,
                                   wdgc=wdgc,
                                   source=source,
                                   latitude=lat,
                                   longitude=lon,
                                   speed=speed,
                                   precision=precision)

        except Exception as err:
            print(err)
            return HttpResponse("Malformed message!")

        td.save()
        # Return Configurations
        return JsonResponse({
            'Mode': tracker.Mode,
            'Tint': tracker.Tint,
            'TGPS': tracker.TGPS,
            'Tsend': tracker.Tsend,
        })
