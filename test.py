import requests

url = "http://translate.google.cn/translate_a/single"
origintext = "Por cierto, pueden cambiar el 2do diseño para que rompa la bedrock justo debajo al girar el pistón que"
querystring = {"client": "gtx", "dt": "t", "dj": "1", "ie": "UTF-8", "sl": "auto", "tl": "zh_CN",
               "q": origintext}

payload = ""
headers = {
    'User-Agent': "PostmanRuntime/7.11.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "2fb29936-69ef-405e-be97-02ba2bf646ad,2d2b4882-edd6-4b30-9cb1-0802f7a89458",
    'Host': "translate.google.cn",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}

response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

print(response['sentences'][0]['trans'])
