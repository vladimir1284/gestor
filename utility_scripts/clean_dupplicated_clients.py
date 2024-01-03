# Step 1: Import necessary modules and models
from utils.models import Order
from rent.models.lease import Contract, Due, LesseeData, Payment
from services.models import DebtStatus, Expense, PendingPayment
from users.models import Associated
from django.db.models import Count

DRY_RUN = False

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

    duplicates = Associated.objects.filter(
        phone_number=phone_number_value).exclude(id=remaining_instance.id)
    print(
        f"Remaining instance id: {remaining_instance.id} for phone: {phone_number_value}, with {len(duplicates)} duplicates")
    for instance in duplicates:
        for field, value in instance.__dict__.items():
            if field != 'id' and field != '_state' and value and not remaining_instance_data[field]:
                setattr(remaining_instance, field, value)
                print(
                    f"Field: {field} with value: {value} saved into remaining instance!")
        if not DRY_RUN:
            remaining_instance.save()

        # Step 6: Update the references to the deleted instances in the 'Order' instances from the utils app to reference the remaining instance

        order_to_update = Order.objects.filter(associated=instance)
        if (len(order_to_update) > 0):
            print("Orders to update")
            print(order_to_update)
        ld_to_update = LesseeData.objects.filter(associated=instance)
        if (len(ld_to_update) > 0):
            print("LesseeDatas to update")
            print(ld_to_update)
        expense_to_update = Expense.objects.filter(associated=instance)
        if (len(expense_to_update) > 0):
            print("Expenses to update")
            print(expense_to_update)
        ds_to_update = DebtStatus.objects.filter(client=instance)
        if (len(ds_to_update) > 0):
            print("DebtStatus to update")
            print(ds_to_update)
        due_to_update = Due.objects.filter(client=instance)
        if (len(due_to_update) > 0):
            print("Dues to update")
            print(due_to_update)
        payment_to_update = Payment.objects.filter(client=instance)
        if (len(payment_to_update) > 0):
            print("Payments to update")
            print(payment_to_update)
        pp_to_update = PendingPayment.objects.filter(client=instance)
        if (len(pp_to_update) > 0):
            print("Pending payments to update")
            print(pp_to_update)
        contracts_to_update = Contract.objects.filter(lessee=instance)
        if (len(contracts_to_update) > 0):
            print("Contracts to update")
            print(contracts_to_update)

        if not DRY_RUN:
            contracts_to_update.update(lessee=remaining_instance)
            pp_to_update.update(client=remaining_instance)
            payment_to_update.update(client=remaining_instance)
            due_to_update.update(client=remaining_instance)
            ds_to_update.update(client=remaining_instance)
            expense_to_update.update(associated=remaining_instance)
            ld_to_update.update(associated=remaining_instance)
            order_to_update.update(associated=remaining_instance)

    # Step 7: Delete the duplicated instances (excluding the remaining instance) from the database

    associated_to_delete = Associated.objects.filter(phone_number=phone_number_value).exclude(
        id=remaining_instance.id)
    print("Associateds to be deleted:")
    print([x.id for x in associated_to_delete])
    if not DRY_RUN:
        associated_to_delete.delete()
