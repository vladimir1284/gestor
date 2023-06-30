from django.db import migrations, models
import django.db.models.deletion


def set_manufacturer_null(apps, schema_editor):
    Trailer = apps.get_model('rent', 'Trailer')
    Trailer.objects.update(manufacturer=None)


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0002_tracker_trackerupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('url', models.URLField()),
                ('icon', models.ImageField(blank=True,
                 upload_to='images/manufacturers')),
            ],
        ),
        migrations.RemoveField(
            model_name='trailer',
            name='image',
        ),
        migrations.CreateModel(
            name='TrailerPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='images/equipment')),
                ('trailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='trailer_picture', to='rent.trailer')),
            ],
        ),
        migrations.AlterField(
            model_name='trailer',
            name='manufacturer',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rent.manufacturer'),
        ),
        migrations.RunPython(set_manufacturer_null),
    ]
