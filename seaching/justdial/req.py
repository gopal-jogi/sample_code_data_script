import requests
import time

# Generate dynamic timestamp
current_time = int(time.time())

# Common cookies and headers for both requests
cookies = {
    '_ctok': 'd9d78a155cc331723840239544rwrDkqDh94xA5ssoghorlxtC4wp33CgwB9rC',
    'deviceId': 'd9d78a155cc331723840239544rwrDkqDh94xA5ssoghorlxtC4wp33CgwB9rC',
    # Add other cookies here as necessary
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.justdial.com',
    'referer': 'https://www.justdial.com/india',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    # Add other headers here as necessary
}

# First API call to get `lid`
try:
    first_api_url = 'https://www.justdial.com/india/api/wrapi?apiname=01sep2022&apifile=callallocate&is_verified=0&wap=7&source=7&searchReferrer=gen%7Clst&utm_source=&utm_medium=&version=2.7&jdmart=1&mobile='  # Replace with actual first API URL
    first_api_params = {
        'apiname': 'getLid',  # Replace with actual parameter names
        'search_time': current_time,
        'deviceId': cookies['_ctok'],
    }
    first_response = requests.post(first_api_url, params=first_api_params, cookies=cookies, headers=headers)
    first_response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the response to extract `lid`
    first_response_data = first_response.json()
    lid = first_response_data.get('lid')  # Adjust key as per the response structure

    if not lid:
        raise ValueError("Failed to retrieve 'lid' from the first API response")

    print("Retrieved 'lid':", lid)

except requests.exceptions.RequestException as e:
    print("Error during the first API request:", str(e))
    exit(1)

# Second API call using `lid`
try:
    second_api_url = 'https://www.justdial.com/india/api/wrapi'  # Replace with actual second API URL
    headers['dil']=lid

    second_api_params = {
        'apiname': '20march2020',
        'apifile': 'autosuggest',
        'search': 'a',
        'supplier': '1',
        'city': 'India',
        'wap': '7',
        'source': '7',
        'case': 'b2b_search',
        'type': 'auto_both',
        'max': '10',
        'version': '5.0',
        'search_time': current_time,
        'deviceId': cookies['_ctok'],
    }
    second_api_data = {
        'lid': lid,  # Use the `lid` from the first API
    }
    second_response = requests.post(second_api_url, params=second_api_params, cookies=cookies, headers=headers, data=second_api_data)
    second_response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse and print the second API response
    second_response_data = second_response.json()
    print("Second API Response:", second_response_data)

except requests.exceptions.RequestException as e:
    print("Error during the second API request:", str(e))
