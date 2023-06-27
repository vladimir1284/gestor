import json
from django.core.exceptions import ObjectDoesNotExist
from rent.models.tracker import Tracker
from rent.models.vehicle import Trailer

# Open the JSON file containing the tracker data
with open('trackers.json') as f:
    serialized_trackers = f.read()

# Deserialize the JSON data into a list of Python dictionaries
deserialized_trackers = json.loads(serialized_trackers)

# Loop over the deserialized trackers and create new Tracker objects
for tracker_data in deserialized_trackers:
    # Map the data to the new Tracker model
    trailer_bin_number = tracker_data['fields'].get('trailer_bin_number', '')
    trailer = None
    if trailer_bin_number:
        try:
            trailer = Trailer.objects.get(vin=trailer_bin_number)
        except ObjectDoesNotExist:
            pass
    last_update = tracker_data['fields'].get('last_update', None)
    imei = tracker_data['fields']['imei']
    device_password = tracker_data['fields']['device_password']
    device_id = tracker_data['fields'].get('device_id', None)
    mode = tracker_data['fields']['Mode']
    tint = tracker_data['fields']['Tint']
    t_gps = tracker_data['fields']['TGPS']
    t_send = tracker_data['fields']['Tsend']

    # Create a new Tracker object with the mapped data
    new_tracker = Tracker(trailer=trailer,
                          imei=imei,
                          device_password=device_password,
                          device_id=device_id,
                          Mode=mode,
                          Tint=tint,
                          TGPS=t_gps,
                          Tsend=t_send)
    new_tracker.save()
