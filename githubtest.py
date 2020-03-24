import requests

url = "https://api.github.com/repos/Aye10032/YouTubeDownLoad/releases/latest"

proxy = {
    'http': 'http://127.0.0.1:10809'
}
try:
    response = requests.request("GET", url)
except requests.exceptions.ConnectionError:
    response = requests.request("GET", url, proxies=proxy)
rjs = response.json()

print(rjs)
