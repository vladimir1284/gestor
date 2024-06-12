from django.contrib import admin

from .models.cost import RentalCost
from .models.cost import RentalCostCategory
from .models.lease import Contract
from .models.lease import Due
from .models.lease import HandWriting
from .models.lease import Inspection
from .models.lease import Lease
from .models.lease import LeaseDeposit
from .models.lease import LeaseDocument
from .models.lease import LesseeData
from .models.lease import Note
from .models.lease import Payment
from .models.lease import SecurityDepositDevolution
from .models.lease import Tire
from .models.tracker import Tracker
from .models.tracker import TrackerUpload
from .models.trailer_deposit import TrailerDeposit
from .models.trailer_deposit import TrailerDepositTrace
from .models.vehicle import Manufacturer
from .models.vehicle import Trailer
from .models.vehicle import TrailerDocument
from .models.vehicle import TrailerPicture
from .models.vehicle import TrailerPlates
from rent.models.deposit_discount import DepositDiscount

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
admin.site.register(Note)
admin.site.register(RentalCost)
admin.site.register(RentalCostCategory)
admin.site.register(TrailerDeposit)
admin.site.register(TrailerDepositTrace)
admin.site.register(DepositDiscount)
