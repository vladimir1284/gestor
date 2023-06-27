import pickle
from datetime import datetime
from rent.models.tracker import TrackerUpload, Tracker


def import_tracker_data_from_pickle(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        for imei, tracker_data_list in data.items():
            try:
                tracker = Tracker.objects.get(imei=imei)
            except Tracker.DoesNotExist:
                print(f"No tracker found with imei '{imei}'")
                continue

            for tracker_data in tracker_data_list:

                tracker_upload = TrackerUpload(
                    tracker=tracker,
                    timestamp=tracker_data.get('timestamp'),
                    sequence=tracker_data.get('sequence'),
                    charging=tracker_data.get('charging'),
                    battery=tracker_data.get('battery'),
                    wur=tracker_data.get('wur'),
                    wdgc=tracker_data.get('wdgc'),
                    source=tracker_data.get('source', 'LTE'),
                    latitude=tracker_data.get('latitude'),
                    longitude=tracker_data.get('longitude'),
                    speed=tracker_data.get('speed'),
                    precision=tracker_data.get('precision'),
                    mcc=tracker_data.get('mcc'),
                    mnc=tracker_data.get('mnc'),
                    lac=tracker_data.get('lac'),
                    cellid=tracker_data.get('cellid')
                )
                tracker_upload.save()

        print("Data import successful.")

    except FileNotFoundError:
        print("File not found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Usage example:
file_path = 'tracker_data.pkl'
import_tracker_data_from_pickle(file_path)
