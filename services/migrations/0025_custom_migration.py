import os
from django.db import migrations
from gdstorage.storage import GoogleDriveStorage

drive = GoogleDriveStorage()

base_dir = "media/"
if not (os.path.exists(base_dir) and os.path.exists(base_dir+"images")):
    os.makedirs(base_dir+"images")

def forwards_func(apps, schema_editor):
    folder = "images/expenses/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Expense = apps.get_model("services", "Expense")
    db_alias = schema_editor.connection.alias
    for item in Expense.objects.using(db_alias).all():
        if item.image.name and drive.exists(item.image.name):
            ext_path = item.image.name
            if not item.image.name.startswith(folder):
                fname = str(item.image.name).split("/")[-1]
                item.image.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.image.name, "wb") as local_file:
                    local_file.write(ext_file.read())

    folder = "images/services/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    ServicePicture = apps.get_model("services", "ServicePicture")
    db_alias = schema_editor.connection.alias
    for item in ServicePicture.objects.using(db_alias).all():
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
        ('services', '0024_alter_expense_image_alter_servicepicture_image'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
