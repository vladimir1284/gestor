from django.urls import path

from whatsapp.views.whatsapp import whatsapp_bot

urlpatterns = [
    path("bot", whatsapp_bot, name="bot"),
]
