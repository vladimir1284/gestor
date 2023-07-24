from django.contrib import admin
from .models.vehicle import (
    Trailer,
    TrailerPicture,
    Manufacturer,
    TrailerDocument,
)
from .models.tracker import (
    Tracker,
    TrackerUpload,
)
from .models.lease import (
    HandWriting,
    ContractDocument,
    Lease,
    LesseeData,
)

admin.site.register(Trailer)
admin.site.register(Tracker)
admin.site.register(TrackerUpload)
admin.site.register(TrailerPicture)
admin.site.register(TrailerDocument)
admin.site.register(Manufacturer)
admin.site.register(Lease)
admin.site.register(HandWriting)
admin.site.register(ContractDocument)
admin.site.register(LesseeData)
