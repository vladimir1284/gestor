from django.contrib import admin
from .models.vehicle import (
    Trailer,
    TrailerPicture,
    Manufacturer,
    TrailerDocument,
    TrailerPlates
)
from .models.tracker import (
    Tracker,
    TrackerUpload,
)
from .models.lease import (
    HandWriting,
    Contract,
    LesseeData,
    Inspection,
    Tire,
    Lease,
    Payment,
    Due,
    LeaseDocument,
    LeaseDeposit,
    SecurityDepositDevolution,
)

admin.site.register(Trailer)
admin.site.register(Tracker)
admin.site.register(TrackerUpload)
admin.site.register(TrailerPicture)
admin.site.register(TrailerDocument)
admin.site.register(Manufacturer)
admin.site.register(Contract)
admin.site.register(HandWriting)
admin.site.register(LesseeData)
admin.site.register(Inspection)
admin.site.register(Tire)
admin.site.register(Lease)
admin.site.register(Payment)
admin.site.register(Due)
admin.site.register(LeaseDocument)
admin.site.register(LeaseDeposit)
admin.site.register(TrailerPlates)
admin.site.register(SecurityDepositDevolution)
