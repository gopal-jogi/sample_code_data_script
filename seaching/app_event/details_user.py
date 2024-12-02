import requests
from pymongo import MongoClient
import time

client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')
db = client['emp_info']
fetch_data_col = db['user_list']
output_col = db['user_details']

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
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

user_list = fetch_data_col.find()

count = 1
for user in user_list:
    for user_data in user['attendees']:
        user_id = user_data['id']
        name= user_data['name']
        
        # Skip the first 2000 users
        if count <= 0:
            count += 1
            continue
        if output_col.count_documents({'username': name}) >= 1:
            print("duplicate")
            continue
        
        # Fetch user details from the API
        response = requests.get(f'https://hybrid.chkdin.com/visitorv2/userinfov2/117859/{user_id}/394600', headers=headers, verify=False)
        
        # Ensure that the response is valid and contains the data
        if response.status_code == 200:
            user_info = response.json()
            if 'qr_code' in user_info:
                # Check if qr_code already exists in the collection
                if output_col.count_documents({'qr_code': user_info['qr_code']}) == 0:
                    user_info['flag'] = "post_event"
                    # Insert the new document only if qr_code is unique
                    output_col.insert_one(user_info)
                    print(f"Data for user_id={user_id} inserted into MongoDB.")
                else:
                    print(f"Duplicate found for qr_code={user_info['qr_code']}. Skipping insertion.")
            else:
                print(f"Missing 'qr_code' for user_id={user_id}. Skipping.")
        else:
            print(f"Failed to fetch data for user_id={user_id}. HTTP Status Code: {response.status_code}")
        
        # Respect rate limiting by adding a sleep between requests
        time.sleep(3)

client.close()
