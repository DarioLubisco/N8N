import urllib.request
import json

url = 'https://openrouter.ai/api/v1/models'
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    for model in data['data']:
        if 'hermes' in model['id'].lower() and 'nousresearch' in model['id'].lower():
            print(f"{model['id']}")
