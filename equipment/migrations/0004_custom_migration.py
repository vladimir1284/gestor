import os
from django.db import migrations
from gdstorage.storage import GoogleDriveStorage

drive = GoogleDriveStorage()

base_dir = "media/"
if not (os.path.exists(base_dir) and os.path.exists(base_dir+"images")):
    os.makedirs(base_dir+"images")

def forwards_func(apps, schema_editor):
    folder = "images/equipment/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Trailer = apps.get_model("equipment", "Trailer")
    db_alias = schema_editor.connection.alias
    for item in Trailer.objects.using(db_alias).all():
        if item.image.name and drive.exists(item.image.name):
            ext_path = item.image.name
            if not item.image.name.startswith(folder):
                fname = str(item.image.name).split("/")[-1]
                item.image.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.image.name, "wb") as local_file:
                    local_file.write(ext_file.read())

    folder = "images/equipment/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Vehicle = apps.get_model("equipment", "Vehicle")
    db_alias = schema_editor.connection.alias
    for item in Vehicle.objects.using(db_alias).all():
        if item.image.name and drive.exists(item.image.name):
            ext_path = item.image.name
            if not item.image.name.startswith(folder):
                fname = str(item.image.name).split("/")[-1]
                item.image.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.image.name, "wb") as local_file:
                    local_file.write(ext_file.read())


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0003_alter_trailer_year_alter_vehicle_year'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
