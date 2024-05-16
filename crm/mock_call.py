import requests

# Define the URL of the Django view
url = "http://localhost:8000/erp/crm/handle-call"

# Define the data to be sent in the POST request
data = {
    "Called": "+12176347289",
    "ToState": "IL",
    "CallerCountry": "test_caller_country",
    "Direction": "test_direction",
    "CallerState": "test_caller_state",
    "ToZip": "test_to_zip",
    "CallSid": "test_call_sid",
    "To": "test_to_phone_number",
    "CallerZip": "test_caller_zip",
    "ToCountry": "US",
    "CallToken": "test_call_token",
    "CalledZip": "test_called_zip",
    "ApiVersion": "test_api_version",
    "CalledCity": "test_called_city",
    "CallStatus": "test_call_status",
    "From": "+5351832447",
    "AccountSid": "test_account_sid",
    "CalledCountry": "test_called_country",
    "CallerCity": "test_caller_city",
    "ToCity": "test_to_city",
    "FromCountry": "CU",
    "Caller": "test_caller_phone_number",
    "FromCity": "test_from_city",
    "CalledState": "test_called_state",
    "FromZip": "test_from_zip",
    "FromState": "test_from_state",
}

# Make the POST request
response = requests.post(url, data=data)

# Print the response status code
print("Response Status Code:", response.status_code)
