import requests
from pymongo import MongoClient
import time
# MongoDB setup
client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')
db = client['emp_info']  # Replace with your database name
collection = db['user_list']  # Replace with your collection name

# Headers (make sure to update any required fields)
headers = {
    'Host': 'hybrid.chkdin.com',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Sec-Fetch-Site': 'same-site',
    'Origin': 'https://bts2024.chkdin.com',
    'Sec-Fetch-Dest': 'empty',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
    'Sec-Fetch-Mode': 'cors',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1 PWAShell',
    'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyRW1haWwiOiJyYXZpQHppbnRsci5jb20iLCJBUElfVElNRSI6MTczMDcxODM2MX0.lvJtcY1pHe3o7Yz4ZRBe-R2aAFQpL0pEuoL25NQfVtE',
#     # 'Accept-Encoding': 'gzip, deflate, br',  # Replace with your actual token
    'Connection': 'keep-alive',
    
}

# Loop through p values from 0 to 20
for p_value in range(1, 420):
    params = {
        'p': str(p_value),
    }
    
    try:
        response = requests.get(
            'https://hybrid.chkdin.com/visitorv2/allattendees_innerv2/117859/394600',
            params=params,
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
        print("error",response.raise_for_status())  # Check for HTTP request errors
        data = response.json()
        print
        # Insert data into MongoDB
        collection.insert_one(data)
        time.sleep(5)  # Add a delay to avoid flooding the server
        print(f"Data for p={p_value} inserted into MongoDB.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for p={p_value}: {e}")

# Close the MongoDB connection
client.close()
