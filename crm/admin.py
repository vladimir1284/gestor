from django.contrib import admin
from .models.twilio_model import (TwilioCall)
from .models.crm_model import (FlaggedCalls)



admin.site.register(TwilioCall)
admin.site.register(FlaggedCalls)