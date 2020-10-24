import requests

url = "http://api.aye10032.com/videos?has_done=0&need_trans=0"

response = requests.request("GET", url)

done_list = []

for element in response.json()['data']:
    done_list.append('NO.' + str(element['ID']) + ' ' + element['DESCRIPTION'])

print(done_list)
print(done_list[-1])
