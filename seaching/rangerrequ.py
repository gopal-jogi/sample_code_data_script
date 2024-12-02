import requests

# Start a session to persist cookies between requests
session = requests.Session()

# Step 1: Perform a GET request to retrieve the XSRF-TOKEN and initial session cookies
get_url = 'https://pressranger.com/publishers?page=3'
response_get = session.get(get_url)

# Check if the XSRF-TOKEN and session cookies are set after the GET request
initial_cookies = session.cookies.get_dict()
print("Cookies after GET request:", initial_cookies)

# You can now extract the XSRF-TOKEN from the session cookies
xsrf_token = initial_cookies.get('XSRF-TOKEN')
press_ranger_session = initial_cookies.get('press_ranger_session')

# Step 2: Use the updated cookies in the POST request
post_url = 'https://pressranger.com/livewire/update'

# Headers for the POST request (ensure to include the XSRF-TOKEN if necessary)
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://pressranger.com',
    'referer': 'https://pressranger.com/publishers?page=3',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-xsrf-token': xsrf_token,  # Include the XSRF-TOKEN in the headers
}

# JSON data for the POST request
json_data = {
    '_token': xsrf_token,  # Ensure to include the token in the POST data
    'components': [
        {
            'snapshot': '{"data":{"search":null,"countries":[[],{"s":"arr"}],"languages":[[],{"s":"arr"}],"types":[[],{"s":"arr"}],"sectors":[[],{"s":"arr"}],"location":null,"userCountries":[[],{"s":"arr"}],"userLanguages":[[],{"s":"arr"}],"userSectors":[[],{"s":"arr"}],"total":null,"loading":false,"paginators":[{"page":2},{"s":"arr"}]},"memo":{"id":"g56jxUM0030CIx6TMadC","name":"entity-search","path":"publishers","method":"GET","children":[],"scripts":[],"assets":[],"errors":[],"locale":"en"},"checksum":"b8659037aaf3a328ff5555fd5acd932048d54da1e1732f7fdf6d0cc291a241d1"}',
            'updates': {},
            'calls': [
                {
                    'path': '',
                    'method': 'nextPage',
                    'params': [
                        'page',
                    ],
                },
            ],
        },
    ],
}

# Step 2: Perform the POST request using the session with updated cookies and headers
response_post = session.post(post_url, headers=headers, json=json_data)

# Print the response from the POST request
print(response_post.text)

# Verify if the cookies have been updated again after the POST request
updated_cookies = session.cookies.get_dict()
print("Updated Cookies after POST request:", updated_cookies)
