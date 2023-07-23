from django.db.models import Count

# Assuming you have the Order model defined in the 'utils' app
from utils.models import Order

# Step 1: Import necessary modules and models

from users.models import Associated

# Step 2: Find duplicated instances based on the 'phone_number' field

duplicated_phone_numbers = Associated.objects.exclude(phone_number='').values('phone_number').annotate(
    count=Count('id')).filter(count__gt=1)

# Step 3: Loop through each set of duplicated instances

for phone_number in duplicated_phone_numbers:
    phone_number_value = phone_number['phone_number']

    # Step 4: Select one instance to remain (usually the first instance in the set) and store it in a variable

    remaining_instance = Associated.objects.filter(
        phone_number=phone_number_value).first()

    # Step 5: Loop through the remaining instances and copy any missing data to the remaining instance

    remaining_instance_data = remaining_instance.__dict__
    for instance in Associated.objects.filter(phone_number=phone_number_value).exclude(id=remaining_instance.id):
        for field, value in instance.__dict__.items():
            if field != 'id' and field != '_state' and not value and remaining_instance_data[field]:
                setattr(instance, field, remaining_instance_data[field])
        instance.save()

        # Step 6: Update the references to the deleted instances in the 'Order' instances from the utils app to reference the remaining instance

        Order.objects.filter(associated=instance).update(
            associated=remaining_instance)

    # Step 7: Delete the duplicated instances (excluding the remaining instance) from the database

    Associated.objects.filter(phone_number=phone_number_value).exclude(
        id=remaining_instance.id).delete()
