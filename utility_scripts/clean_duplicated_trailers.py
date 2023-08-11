from django.db import transaction
from rent.models.vehicle import Trailer, TrailerDocument, TrailerPicture
from rent.models.lease import Lease
from utils.models import Order


def delete_duplicate_trailers():
    # Get all trailers grouped by VIN
    trailers = Trailer.objects.all().order_by('vin')
    trailers_by_vin = {}
    for trailer in trailers:
        trailers_by_vin.setdefault(trailer.vin, []).append(trailer)

    # Iterate over trailers with duplicate VINs
    for vin, duplicates in trailers_by_vin.items():
        if len(duplicates) > 1:
            print(f"Deleting duplicate trailers for VIN: {vin}")
            remaining_trailer = duplicates[0]
            deleted_trailers = duplicates[1:]

            # Update references in related models
            update_references(remaining_trailer, deleted_trailers)

            # Delete duplicate trailers
            with transaction.atomic():
                for trailer in deleted_trailers:
                    trailer.delete()
            print(
                f"Deleted {len(deleted_trailers)} duplicate trailers for VIN: {vin}")


def update_references(remaining_trailer, deleted_trailers):
    # Update references in Order model
    Order.objects.filter(trailer__in=deleted_trailers).update(
        trailer=remaining_trailer)

    # Update references in TrailerDocument model
    TrailerDocument.objects.filter(
        trailer__in=deleted_trailers).update(trailer=remaining_trailer)

    # Update references in TrailerPicture model
    TrailerPicture.objects.filter(
        trailer__in=deleted_trailers).update(trailer=remaining_trailer)

    # Update references in Lease model
    Lease.objects.filter(
        trailer__in=deleted_trailers).update(trailer=remaining_trailer)


delete_duplicate_trailers()
