from django.urls import path
from .views import vehicle, tracker


urlpatterns = [
    # -------------------- Vehicle ----------------------------
    path('create-trailer', vehicle.create_trailer, name='create-trailer'),
    path('list-trailer', vehicle.list_equipment, name='list-trailer'),
    path('select-trailer', vehicle.select_trailer, name='select-trailer'),
    path('update-trailer/<id>', vehicle.update_trailer, name='update-trailer'),
    path('delete-trailer/<id>', vehicle.delete_trailer, name='delete-trailer'),
    path('detail-trailer/<id>', vehicle.detail_trailer, name='detail-trailer'),
    path('select-towit', vehicle.select_towit, name='select-towit'),
    # -------------------- Tracker ----------------------------
    path('create-tracker/<int:trailer_id>',
         tracker.TrackerCreateView.as_view(), name='create-tracker'),
    path('update-tracker/<slug:pk>',
         tracker.TrackerUpdateView.as_view(), name='update-tracker'),
    path('delete-tracker/<int:id>',  tracker.delete_tracker, name='delete-tracker'),
    path('detail-tracker/<int:id>',  tracker.tracker_detail, name='detail-tracker'),
    path('trackers-map/',  tracker.trackers, name='trackers-map'),
    path('trackers/',  tracker.trackers_table, name='trackers-table'),
    path('tracker-upload', tracker.tracker_upload, name='tracker-upload'),
]
