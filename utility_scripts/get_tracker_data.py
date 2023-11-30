import requests
import pickle
from rent.models.tracker import TrackerUpload, Tracker

# Define the URLs that you want to get information from.
upload_url = "https://trailerrental.pythonanywhere.com/towit/get_upload_data/{}"
tracker_url = "https://trailerrental.pythonanywhere.com/towit/get_tracker_data/{}"

# Define a function to get the data from the URLs.


def get_data(url):
    response = requests.get(url)
    return response.json()

# Define a function to save the data to a file.


def save_data(data, filename):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

# Define a function to load the data from a file or assign 0 if the file is not found.


def load_data(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return 0


# Load the last_upload_id from the pickle file or assign 0 if the file is not found.
last_upload_id = load_data("last_upload_id.pkl")

# Load the last_data_id from the pickle file or assign 0 if the file is not found.
last_data_id = load_data("last_data_id.pkl")

# Get the data from the URLs.
upload_data = get_data(upload_url.format(last_upload_id))
tracker_data = get_data(tracker_url.format(last_data_id))

# Update last ids
if len(upload_data) > 0:
    last_upload_id = upload_data[0]['pk']
    save_data(last_upload_id, "last_upload_id.pkl")
else:
    print("No new data on tracker upload!")

if len(tracker_data) > 0:
    last_data_id = tracker_data[0]['pk']
    save_data(last_data_id, "last_data_id.pkl")
else:
    print("No new data on tracker data!")

# Save the data to the database.
# Save new format
for data in upload_data:
    TrackerUpload.objects.create(
        tracker=Tracker.objects.get(id=data['fields']['tracker']),
        timestamp=data['fields']['timestamp'],
        sequence=data['fields']['sequence'],
        charging=data['fields']['charging'],
        battery=data['fields']['battery'],
        wur=data['fields']['wur'],
        wdgc=data['fields']['wdgc'],
        source=data['fields']['source'],
        latitude=data['fields']['latitude'],
        longitude=data['fields']['longitude'],
        speed=data['fields']['speed'],
        precision=data['fields']['precision'],
        mcc=data['fields']['mcc'],
        mnc=data['fields']['mnc'],
        lac=data['fields']['lac'],
        cellid=data['fields']['cellid']
    )

# Save old format
for data in upload_data:
    TrackerUpload.objects.create(
        tracker=Tracker.objects.get(id=data['fields']['tracker']),
        timestamp=data['fields']['timestamp'],
        sequence=data['fields']['sequence'],
        charging=data['fields']['charging'],
        battery=data['fields']['battery'],
        source='GPS',
        latitude=data['fields']['latitude'],
        longitude=data['fields']['longitude'],
        speed=data['fields']['speed']
    )
