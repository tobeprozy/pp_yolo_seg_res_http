import requests
import json
import os
import base64
import re

url = "http://172.21.2.85:5000/result"

payload = json.dumps({})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
results = response.json()

save_dir = './img_with_results/'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for result in results:
    
    for key in result.keys():
        if re.match(r'^gt_', key):
            print(key)
            img_name = key
            break
    jpg_base64 = result.get('jpg_base64')
    if img_name and jpg_base64:
        image_data = base64.b64decode(jpg_base64)
        save_path = os.path.join(save_dir, f'{img_name}.jpg')
        with open(save_path, 'wb') as f:
            f.write(image_data)
