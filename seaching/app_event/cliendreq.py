import requests
import pymongo
import time

# Set up MongoDB connection
client = pymongo.MongoClient('mongodb://c8f1423c9e7a4f8d8b4d9d5c3a2b1e6f7d9c0e2f1d3a4b5c6d7e8f9a0b1c2d3e:e4f8a6b9d7c2a1b3c5d6e9f7a8b0c1d4e2f3a5b7c8d9e0f1a6b7c4d3e5f8g7h2@10.128.0.4:27017/admin')
db = client['plexconcil']
collection = db['directories']

# Create a unique index on the 'page' field to ensure uniqueness
collection.create_index('page', unique=True)

# Define cookies and headers
cookies = {
    '_gid': 'GA1.2.830038356.1731388981',
    '_fbp': 'fb.1.1731388982691.914616453368428006',
    'ci_session': '5f28115a4334b4076b556367c1d575dd19cfa7da',
    '_ga_ZCKE38MPDG': 'GS1.1.1731412267.2.1.1731412270.0.0.0',
    '_ga': 'GA1.2.618690159.1731388980',
    '_gat_gtag_UA_146157274_1': '1',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://plexconcil.org',
    'Referer': 'https://plexconcil.org/member/directory',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# Base data for the POST request
data = {
    'product': '',
    'cname': '',
    'city': '',
    'region': '',
    'sort': '',
    'page': '1',
}

# Iterate over pages 1 to 105
for page_num in range(1, 106):
    data['page'] = str(page_num)
    try:
        # Send POST request
        response = requests.post(
            'https://plexconcil.org/member/getDirectories',
            cookies=cookies,
            headers=headers,
            data=data
        )
        response.raise_for_status()  # Raise an error for bad status codes

        json_response = response.json()
        # Prepare the document to be inserted
        document = {
            'page': page_num,
            'status': response.status_code,
            'response': json_response,
        }

        # Insert into MongoDB
        collection.insert_one(document)
        print(f"Page {page_num} stored successfully.")

    except pymongo.errors.DuplicateKeyError:
        print(f"Page {page_num} already exists in the database.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed on page {page_num}: {e}")
    except Exception as e:
        print(f"An error occurred on page {page_num}: {e}")

    # Wait for 3 seconds before the next request
    time.sleep(3)
