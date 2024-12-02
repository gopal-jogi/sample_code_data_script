import requests

headers = {
    'Host': 'hybrid.chkdin.com',
    'Accept': '*/*',
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

response = requests.get('https://hybrid.chkdin.com/visitorv2/downloadVCard/117859/065498', headers=headers, verify=False)
print(response.text)