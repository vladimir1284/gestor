from equipment.models import Trailer
from rent.models import Trailer as NewTrailer
from utils.models import Order

trailers = Trailer.objects.all()

id_list = []

for trailer in trailers:
    last_service = Order.objects.filter(trailer=trailer).last()
    if last_service.company:
        print("--------------------------------")
        print(F"Company: {last_service.company}")
        new_trailers = NewTrailer.objects.filter(vin=trailer.vin)
        if last_service.company.name.lower().find("towit") != -1:
            if last_service.associated:
                print(F"Client: {last_service.associated}")
            first = True
            for new_trailer in new_trailers:
                if (first):
                    print(
                        F"Found vin:{new_trailer.vin}, id: {new_trailer.id}!")
                    first = False
                    id_list.append(new_trailer.id)
                else:
                    print(
                        F"Deleted vin:{new_trailer.vin}, id: {new_trailer.id}!")
                    new_trailer.delete()
        else:
            for new_trailer in new_trailers:
                print(
                    F"Deleted vin:{new_trailer.vin}, id: {new_trailer.id}!")
                new_trailer.delete()

# Get all the new trailers instances whose IDs are not in the TOWIT list
instances_to_delete = NewTrailer.objects.exclude(id__in=id_list)

# Delete the instances
instances_to_delete.delete()

print("================================================================")
print(F"Found {len(id_list)} trailer from TOWIT!")
