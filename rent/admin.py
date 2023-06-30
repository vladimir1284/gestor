from django.contrib import admin
from .models.vehicle import (
    Trailer,
    TrailerPicture,
    Manufacturer,
)
from .models.tracker import (
    Tracker,
    TrackerUpload
)

admin.site.register(Trailer)
admin.site.register(Tracker)
admin.site.register(TrackerUpload)
admin.site.register(TrailerPicture)
admin.site.register(Manufacturer)
