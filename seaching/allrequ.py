import requests

cookies = {
    '_ga': 'GA1.1.1884270192.1727951314',
    '__stripe_mid': 'bd36022d-d801-4356-b51d-b82f178ff8ea78540a',
    '__stripe_sid': '4997329f-2f3c-4f29-a4b8-f1ef54bd05e7524db8',
    'XSRF-TOKEN': 'eyJpdiI6IjlEYXY1bGl3QXdQTmg1ekJZUXBpMGc9PSIsInZhbHVlIjoiS3Z2bjFId0YrMW5CTlg3Z05CMDBUdXJwbWFpM3RpWXBveUFvTUF2S0ZHWGl1S2lFMUdhUGNvMS8wM3V6RFMybzhVYlViRVBhcDJCN2xDSG9iVjVrZkFWYkhhcHZpdGR4Mm01VG1vNkpMTTBJZmdIWUFTVGdNaFZTMWc0eEkyeU8iLCJtYWMiOiJjYmYyNjE1MTVhNDE3NzE3OTA5MWQzNzM2Y2U4ZDUzOWU4OTUxODIxYTI2ZWI3N2MzOTIyODQ4ZmU5NzFlMTkxIiwidGFnIjoiIn0%3D',
    'press_ranger_session': 'eyJpdiI6IkJCcVMrQ3AwRmR6YXYrYTExalBhSWc9PSIsInZhbHVlIjoiYnZHOW94RjE2RHdmbGp5WFJjVWJhOUZ6aXp2VCtId2JyenlDNGM4UXFlekFwNEhzVEdoaWFBazlpUjZhQUFHOHlVVHE2cnM3b05QU083eFYzUGc1TWI3bUVlb3VlSHZ5cHJULys5UUFGZ284cVJuM0pDOGszdmNzaStkRzZFZWgiLCJtYWMiOiI4MDY1YzFjZDhjNWE5ZjBmYzRhYzYyNmQ0Y2FkNjY1Y2ZjYzg2ZjdmZWMxNjdmYmYwNzY0YTMyZGVlZDNlMGI2IiwidGFnIjoiIn0%3D',
    '_ga_Z4XHBSNR19': 'GS1.1.1728035558.3.1.1728036280.0.0.0',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': '_ga=GA1.1.1884270192.1727951314; __stripe_mid=bd36022d-d801-4356-b51d-b82f178ff8ea78540a; __stripe_sid=4997329f-2f3c-4f29-a4b8-f1ef54bd05e7524db8; XSRF-TOKEN=eyJpdiI6IjlEYXY1bGl3QXdQTmg1ekJZUXBpMGc9PSIsInZhbHVlIjoiS3Z2bjFId0YrMW5CTlg3Z05CMDBUdXJwbWFpM3RpWXBveUFvTUF2S0ZHWGl1S2lFMUdhUGNvMS8wM3V6RFMybzhVYlViRVBhcDJCN2xDSG9iVjVrZkFWYkhhcHZpdGR4Mm01VG1vNkpMTTBJZmdIWUFTVGdNaFZTMWc0eEkyeU8iLCJtYWMiOiJjYmYyNjE1MTVhNDE3NzE3OTA5MWQzNzM2Y2U4ZDUzOWU4OTUxODIxYTI2ZWI3N2MzOTIyODQ4ZmU5NzFlMTkxIiwidGFnIjoiIn0%3D; press_ranger_session=eyJpdiI6IkJCcVMrQ3AwRmR6YXYrYTExalBhSWc9PSIsInZhbHVlIjoiYnZHOW94RjE2RHdmbGp5WFJjVWJhOUZ6aXp2VCtId2JyenlDNGM4UXFlekFwNEhzVEdoaWFBazlpUjZhQUFHOHlVVHE2cnM3b05QU083eFYzUGc1TWI3bUVlb3VlSHZ5cHJULys5UUFGZ284cVJuM0pDOGszdmNzaStkRzZFZWgiLCJtYWMiOiI4MDY1YzFjZDhjNWE5ZjBmYzRhYzYyNmQ0Y2FkNjY1Y2ZjYzg2ZjdmZWMxNjdmYmYwNzY0YTMyZGVlZDNlMGI2IiwidGFnIjoiIn0%3D; _ga_Z4XHBSNR19=GS1.1.1728035558.3.1.1728036280.0.0.0',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://pressranger.com/publishers',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

response = requests.get('https://pressranger.com/publishers/techcrunch', cookies=cookies, headers=headers)
print(response.text)