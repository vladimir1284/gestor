from equipment.models import Trailer
from rent.models import Trailer as NewTrailer

trailers = Trailer.objects.all()

for trailer in trailers:
    new_trailer = NewTrailer.objects.create(year=trailer.year,
                                            vin=trailer.vin,
                                            note=trailer.note,
                                            plate=trailer.plate,
                                            cdl=trailer.cdl,
                                            type=trailer.type,
                                            manufacturer=trailer.manufacturer,
                                            axis_number=trailer.axis_number,
                                            load=trailer.load)
