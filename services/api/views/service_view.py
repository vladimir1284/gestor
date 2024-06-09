from rest_framework import permissions
from rest_framework import viewsets

from services.api.serializer.service import ServiceSerializer
from services.models import Service


class ServiceView(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ["GET"]
