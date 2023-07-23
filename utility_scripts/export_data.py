import pickle
from datetime import datetime, timedelta
from towit.model.tracker import Tracker, TrackerUpload

# Get a list of all the different tracker models
trackers = Tracker.objects.all()

# Create an empty dictionary to hold the data for each tracker model
data = {}

# Loop through each tracker model and get the most recent 30 TrackerUpload instances
for tracker in trackers:
    if tracker:
        tracker_data = TrackerUpload.objects.filter(tracker=tracker).order_by('-timestamp')[:30]
        data.setdefault(tracker.imei, list(tracker_data.values()))

# Export the data as a JSON file
with open('tracker_data.pkl',  'wb') as f:
	pickle.dump(data, f)
