from django.db import migrations

def update_order_position(apps, schema_editor):
    Order = apps.get_model('utils', 'Order')
    orders_to_update = Order.objects.filter(status__in=['pending', 'processing'])
    for order in orders_to_update:
      
        new_position_value = order.position
        positions = ['1', '2', '3', '4', '5', '6', '7', '8']

        if new_position_value in positions:
            order.position = new_position_value
            order.save()
        elif new_position_value == None:
            order.position = 'storage'

    orders_to_nullify = Order.objects.filter(status__in=['complete', 'decline'])
    for order in orders_to_nullify:
        order.position = 'storage'
        order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('services','0001_initial')
    ]

    operations = [
        migrations.RunPython(update_order_position),
    ]