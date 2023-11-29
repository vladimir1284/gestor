import requests

imei = 865235031045004
seq = 5
mode = 1
event = 0
lat = 29.7919
lon = -95.30965
speed = 12
heading = 21
sats = 5
vbat = 3111  # mV

msg = f"{imei},{seq},{mode},{event},{lat},{lon},{speed},{heading},{sats},{vbat}"

response = requests.post("http://localhost:8888/towit/tracker_data", data=msg)
if response.status_code == 200:
    print("ok")
else:
    print("Error posting data to remote url!")

imei = 865235030873836
seq = 6
charging = 1
vbat = 3712  # mV
wur = 0  # WakeUp reason
wdgc = 3  # Watchdog resets count
source = "GPS"  # LTE or GPS
lat = 29.7919
lon = -95.30965
speed = 12
precision = 20

msg = f"{imei},{seq},{charging},{vbat},{wur},{wdgc},{source},{lat},{lon},{speed},{precision}"

response = requests.post("http://localhost:8888/towit/upload_data", data=msg)
if response.status_code == 200:
    print("ok")
else:
    print("Error posting data to remote url!")
