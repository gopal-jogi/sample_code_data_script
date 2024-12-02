import requests
 
cookies = {
    'vtoken': '6706377d1cfa64478b57ad39a9b2321e38'
}
 
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'PHPSESSID=th4dk3oul3vuo09qqe7rb9mv8a; _gid=GA1.2.1934275132.1728460618; _hjSession_2541258=eyJpZCI6IjNlNzRiNGE1LWRmNjYtNGY2YS05YWI2LTQ1ZDY1MjY2OTJhZCIsImMiOjE3Mjg0NjA2MTg0OTksInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; _fbp=fb.1.1728460619909.420898065937305918; _clck=c9tmjn%7C2%7Cfpv%7C0%7C1743; intercom-id-b61auz06=44b7d9d1-f65e-4f4f-ae0e-ceb7fe175c44; intercom-session-b61auz06=; intercom-device-id-b61auz06=c86d04e7-0d15-4825-9d64-0e548415489c; _hjSessionUser_2541258=eyJpZCI6IjBiNTQ4NTQ5LWQ0ZDUtNTc5MS05N2E3LWE2Yjg5ZmIwMmIxNCIsImNyZWF0ZWQiOjE3Mjg0NjA2MTg0OTgsImV4aXN0aW5nIjp0cnVlfQ==; _gcl_au=1.1.1696518342.1728460618.1359477892.1728460636.1728460679; vtoken=6706377d1cfa64478b57ad39a9b2321e38; _gat=1; _ga=GA1.2.1491200192.1728460618; _clsk=18p7l15%7C1728460694383%7C8%7C1%7Cw.clarity.ms%2Fcollect; _ga_BXG1RKV8QE=GS1.1.1728460618.1.1.1728460698.0.0.0',
    'DNT': '1',
    'Origin': 'https://dashboard.easyleadz.com',
    'Referer': 'https://dashboard.easyleadz.com/search',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'User-Token': '6706377d1cfa64478b57ad39',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}
 
data = '{"ukey":"","cind":"","csize":"","ploc":"Abu+Dhabi","page":2,"ctitle":"","token":"d7ce5eea6af7719b551984a8d692a2f2"}'
 
response = requests.post('https://dashboard.easyleadz.com/search_data', cookies=cookies, headers=headers, data=data)
print(response.text)