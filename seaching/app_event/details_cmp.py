import requests
from pymongo import MongoClient
import time

client = MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')
db = client['emp_info']
fetch_data_col = db['cmp_data']
output_col = db['cmp_details']

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

all_cmp_data = fetch_data_col.find()
for cmp_data in all_cmp_data:
    for company in cmp_data['content']:
        cmp_id = company['id']
        # Check if 'name' field exists in company data
        if 'company_name' in company:
            name = company['company_name']
            # Check if the company with the same 'name' already exists in the output collection
            if output_col.count_documents({'name': name}) == 0:
                # If 'name' does not exist, insert the new data
                response = requests.get(f'https://hybrid.chkdin.com/visitorv2/getboothdatav2/117859/394600/{cmp_id}', headers=headers, verify=False)
                
                if response.status_code == 200:
                    inster_data = response.json()
                    inster_data['flag'] = True
                    output_col.insert_one(response.json())
                    print(f"Data for cmp_id={cmp_id} with name={name} inserted into MongoDB.")
                else:
                    print(f"Failed to fetch data for cmp_id={cmp_id}, HTTP Status: {response.status_code}")
            else:
                print(f"Duplicate found for name={name}. Skipping insertion.")
        
        time.sleep(5)

client.close()
