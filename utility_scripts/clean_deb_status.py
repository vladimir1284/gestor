from services.models import DebtStatus


def eliminate_duplicates():
    # Get all DebtStatus instances ordered by client attribute
    debt_statuses = DebtStatus.objects.order_by('client')

    previous_status = None
    duplicates = []

    for status in debt_statuses:
        # Check if current status is the same as the previous one
        if previous_status and status.client == previous_status.client:
            duplicates.append(status)
        previous_status = status

    # Delete the duplicate instances
    for duplicate in duplicates:
        duplicate.delete()

    print(f"{len(duplicates)} duplicate DebtStatus instances deleted.")


# Call the function to eliminate duplicates
eliminate_duplicates()
