import requests
 
cookies = {
    'vtoken': '670632ab774a3341ae46f2bf72053d36a2', 
}
 
headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'prcode=TtwryXxXE7; _clck=17yvo5j%7C2%7Cfpv%7C0%7C1743; intercom-id-b61auz06=37ab42e9-34df-40bf-ab13-0fd5d618e283; intercom-session-b61auz06=; intercom-device-id-b61auz06=0a4215be-f35f-4653-a6df-25bf8c27dc72; B106E2F6056FE017=5b5a2122a497de04be019339b4bac01b; _ga_9NYNPYXV0H=GS1.1.1728456510.1.1.1728456545.25.0.0; _hjSession_2541258=eyJpZCI6ImY3ZmE4ODNkLWJjY2ItNGNmZC1hODExLWZlZmY0ODhkNGYwMyIsImMiOjE3Mjg0NTY1NDgwMDAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxfQ==; _gid=GA1.2.1874287115.1728456548; _fbp=fb.1.1728456548488.924958269189428764; PHPSESSID=gn3ujh3fuckg0nj1afo4mog90i; _hjSessionUser_2541258=eyJpZCI6IjdjYjhhYzU5LWI5ZTItNTdmNC04YjNjLTM4M2Y3MjIzMzRhNiIsImNyZWF0ZWQiOjE3Mjg0NTY1NDc5OTksImV4aXN0aW5nIjp0cnVlfQ==; _gcl_au=1.1.1153500476.1728456548.491409043.1728456734.1728459446; vtoken=670632ab774a3341ae46f2bf72053d36a2; _gat=1; _ga=GA1.2.1307504997.1728456511; _clsk=1vv3dzb%7C1728460417970%7C19%7C1%7Cw.clarity.ms%2Fcollect; _ga_BXG1RKV8QE=GS1.1.1728456547.1.1.1728460418.0.0.0',
    'DNT': '1',
    'Origin': 'https://dashboard.easyleadz.com',
    'Referer': 'https://dashboard.easyleadz.com/search',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'User-Token': '670632ab774a3341ae46f2bf',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}
 
data = '{"ukey":"","cind":"Accounting","csize":"","ploc":"","page":1,"ctitle":"","token":"e786531669f0789305d64a266355bd35"}'
 
response = requests.post('https://dashboard.easyleadz.com/search_data', cookies=cookies, headers=headers, data=data)
print(response.text)