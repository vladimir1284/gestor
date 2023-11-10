import os
from django.db import migrations
from gdstorage.storage import GoogleDriveStorage

drive = GoogleDriveStorage()

base_dir = "media/"
if not (os.path.exists(base_dir) and os.path.exists(base_dir+"images")):
    os.makedirs(base_dir+"images")

def forwards_func(apps, schema_editor):
    folder = "images/costs/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Cost = apps.get_model("costs", "Cost")
    db_alias = schema_editor.connection.alias
    for item in Cost.objects.using(db_alias).all():
        if item.image.name and drive.exists(item.image.name):
            ext_path = item.image.name
            if not item.image.name.startswith(folder):
                fname = str(item.image.name).split("/")[-1]
                item.image.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.image.name, "wb") as local_file:
                    local_file.write(ext_file.read())

    folder = "images/icons/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    CostCategory = apps.get_model("costs", "CostCategory")
    db_alias = schema_editor.connection.alias
    for item in CostCategory.objects.using(db_alias).all():
        if item.icon.name and drive.exists(item.icon.name):
            ext_path = item.icon.name
            if not item.icon.name.startswith(folder):
                fname = str(item.icon.name).split("/")[-1]
                item.icon.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.icon.name, "wb") as local_file:
                    local_file.write(ext_file.read())


class Migration(migrations.Migration):

    dependencies = [
        ('costs', '0006_alter_cost_image'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
