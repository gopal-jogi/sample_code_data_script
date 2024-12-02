import requests
import time

cookies = {
    'st': '84b1016a-8ab6-4e2d-a25b-913ef101f17b',
    '_ga': 'GA1.1.2126092482.1727935798',
    '_hjSessionUser_1484516': 'eyJpZCI6ImNkYWQwY2I1LWJkNTUtNTAwOC1hN2JkLTlmNWQwYWViODEyNiIsImNyZWF0ZWQiOjE3Mjg5NzQ5NDY1OTUsImV4aXN0aW5nIjp0cnVlfQ==',
    'intercom-id-bbh06jpc': '8c0b5177-9638-4293-b649-ebaee63f8598',
    'intercom-device-id-bbh06jpc': '19572a35-4b35-49ac-a595-e06278fb2503',
    '_hjSessionUser_3411820': 'eyJpZCI6IjdhNWZhODMwLTI3N2QtNTgyNi1hYTZiLWE4ODBkOGM3NDgwMyIsImNyZWF0ZWQiOjE3Mjg5NzU3OTEzNjIsImV4aXN0aW5nIjp0cnVlfQ==',
    '_ga_KLHVFHLHS7': 'GS1.1.1728987380.2.0.1728987380.0.0.0',
    '_hjSession_1484516': 'eyJpZCI6IjEwMjljMDBhLTBiMGItNDhlMy1iYTdhLTM4NWE5Y2YyODJhZiIsImMiOjE3Mjk3ODAyNTMyNTgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=',
    'intercom-session-bbh06jpc': '',
    'AID': 'pb6z1ezcmdLaeXfs1AAuM:DKuPkvtJp_Ji8KC6Xunpn',
    '_ga_63RZ0E5CHG': 'GS1.1.1729780228.9.1.1729780550.56.0.0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    # 'cookie': 'st=84b1016a-8ab6-4e2d-a25b-913ef101f17b; _ga=GA1.1.2126092482.1727935798; _hjSessionUser_1484516=eyJpZCI6ImNkYWQwY2I1LWJkNTUtNTAwOC1hN2JkLTlmNWQwYWViODEyNiIsImNyZWF0ZWQiOjE3Mjg5NzQ5NDY1OTUsImV4aXN0aW5nIjp0cnVlfQ==; intercom-id-bbh06jpc=8c0b5177-9638-4293-b649-ebaee63f8598; intercom-device-id-bbh06jpc=19572a35-4b35-49ac-a595-e06278fb2503; _hjSessionUser_3411820=eyJpZCI6IjdhNWZhODMwLTI3N2QtNTgyNi1hYTZiLWE4ODBkOGM3NDgwMyIsImNyZWF0ZWQiOjE3Mjg5NzU3OTEzNjIsImV4aXN0aW5nIjp0cnVlfQ==; _ga_KLHVFHLHS7=GS1.1.1728987380.2.0.1728987380.0.0.0; _hjSession_1484516=eyJpZCI6IjEwMjljMDBhLTBiMGItNDhlMy1iYTdhLTM4NWE5Y2YyODJhZiIsImMiOjE3Mjk3ODAyNTMyNTgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; intercom-session-bbh06jpc=; AID=pb6z1ezcmdLaeXfs1AAuM:DKuPkvtJp_Ji8KC6Xunpn; _ga_63RZ0E5CHG=GS1.1.1729780228.9.1.1729780550.56.0.0',
    'origin': 'https://tracxn.com',
    'priority': 'u=1, i',
    'referer': 'https://tracxn.com/search?q=5',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'x-frontend-app-version': 'nexternalApp-1729770018388-0.2.3',
}

total_results = []
total_count = 22751  # As provided in the response
size = 20  # Number of results per request, adjust if needed
offset = 0 # Starting index

while offset < total_count:
    json_data = {
        'query': {
            'keyword': ['6'],
        'size': size,
    }
    }

    try:
        response = requests.post(
            'https://platform.tracxn.com/api/2.2/ps/companies',
            cookies=cookies,
            headers=headers,
            json=json_data
        )

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            break

        data = response.json()

        # Extracting the results
        results = data.get('result', [])
        if not results:
            print("No more results found.")
            break

        total_results.extend(results)
        print(f"Retrieved {len(total_results)} total results so far.")

        # Update the offset for the next batch
        offset += size

        # Be polite and avoid hitting rate limits
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        break

print(f"Total results retrieved: {len(total_results)}")