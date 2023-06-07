from django.db import migrations, models
import django.db.models.deletion


relations = {}


def get_trailer(apps, schema_editor):
    RentTrailer = apps.get_model('rent', 'Trailer')
    Order = apps.get_model('utils', 'Order')

    for order in Order.objects.all():
        if order.trailer:
            try:
                rent_trailer = RentTrailer.objects.get(
                    vin=order.trailer.vin)
                relations.setdefault(order.id, rent_trailer.id)
            except:
                pass
        order.trailer = None
        order.save()


def set_trailer(apps, schema_editor):
    Order = apps.get_model('utils', 'Order')
    RentTrailer = apps.get_model('rent', 'Trailer')

    for order_id in relations:
        print(order_id, relations[order_id])
        order = Order.objects.get(id=order_id)
        order.trailer = RentTrailer.objects.get(id=relations[order_id])
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rent', '0001_initial'),
        ('utils', '0012_alter_statistics_gpt_insights'),
        ('equipment', '0003_alter_trailer_year_alter_vehicle_year'),
    ]

    operations = [
        migrations.RunPython(get_trailer),
        migrations.AlterField(
            model_name='order',
            name='trailer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='rent.trailer'
            ),
        ),
        migrations.RunPython(set_trailer),
    ]
