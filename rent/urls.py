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
         tracker.TrackerCreateView.as_view(), name='create-trailer-tracker'),
    path('create-tracker/',
         tracker.TrackerCreateView.as_view(), name='create-tracker'),
    path('update-tracker/<slug:pk>',
         tracker.TrackerUpdateView.as_view(), name='update-tracker'),
    path('delete-tracker/<int:id>',  tracker.delete_tracker, name='delete-tracker'),
    path('detail-tracker/<int:id>',  tracker.tracker_detail, name='detail-tracker'),
    path('trackers-map/',  tracker.trackers, name='trackers-map'),
    path('trackers/',  tracker.trackers_table, name='trackers-table'),
    path('tracker-upload', tracker.tracker_upload, name='tracker-upload'),
    # -------------------- Manufacturer ----------------------------
    path('manufacturer-list', vehicle.manufacturer_list, name='manufacturer-list'),
    path('manufacturer-create/', vehicle.manufacturer_create,
         name='manufacturer-create'),
    path('manufacturer-update/<int:pk>',
         vehicle.manufacturer_update, name='manufacturer-update'),
    path('manufacturer-delete/<int:pk>',
         vehicle.manufacturer_delete, name='manufacturer-delete'),
    # -------------------- Manufacturer ----------------------------
    path('picture/create/<int:trailer_id>',
         vehicle.trailer_picture_create, name='trailer-picture-create'),
    path('share_pictures/<ids>',  vehicle.share_pictures, name='share-pictures'),
    path('delete_trailer_pictures/<ids>',
         vehicle.delete_trailer_pictures, name='delete-trailer-pictures'),
]
