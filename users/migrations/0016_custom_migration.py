import os
from django.db import migrations
from gdstorage.storage import GoogleDriveStorage

drive = GoogleDriveStorage()

base_dir = "media/"
if not (os.path.exists(base_dir) and os.path.exists(base_dir+"images")):
    os.makedirs(base_dir+"images")

def forwards_func(apps, schema_editor):
    folder = "images/avatars/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    UserProfile = apps.get_model("users", "UserProfile")
    db_alias = schema_editor.connection.alias
    for item in UserProfile.objects.using(db_alias).all():
        if item.avatar.name and drive.exists(item.avatar.name):
            ext_path = item.avatar.name
            if not item.avatar.name.startswith(folder):
                fname = str(item.avatar.name).split("/")[-1]
                item.avatar.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.avatar.name, "wb") as local_file:
                    local_file.write(ext_file.read())

    folder = "images/avatars/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Company = apps.get_model("users", "Company")
    db_alias = schema_editor.connection.alias
    for item in Company.objects.using(db_alias).all():
        if item.avatar.name and drive.exists(item.avatar.name):
            ext_path = item.avatar.name
            if not item.avatar.name.startswith(folder):
                fname = str(item.avatar.name).split("/")[-1]
                item.avatar.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.avatar.name, "wb") as local_file:
                    local_file.write(ext_file.read())

    folder = "images/avatars/"
    if not os.path.exists(base_dir+folder):
        os.mkdir(base_dir+folder)
    Associated = apps.get_model("users", "Associated")
    db_alias = schema_editor.connection.alias
    for item in Associated.objects.using(db_alias).all():
        if item.avatar.name and drive.exists(item.avatar.name):
            ext_path = item.avatar.name
            if not item.avatar.name.startswith(folder):
                fname = str(item.avatar.name).split("/")[-1]
                item.avatar.name = folder+fname
                item.save()
            with drive.open(ext_path, "rb") as ext_file:
                with open(base_dir+item.avatar.name, "wb") as local_file:
                    local_file.write(ext_file.read())


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_associated_debt'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
