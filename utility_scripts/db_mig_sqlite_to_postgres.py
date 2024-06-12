from django.contrib.contenttypes.models import ContentType
from django.core import management

management.call_command("makemigrations")
management.call_command("migrate")

# management.call_command("flush", interactive=False)

ContentType.objects.all().delete()

management.call_command("loaddata", "data.json")
