import requests
import json
import os
import base64

url = "http://172.24.12.34:5001/result"

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
    frame_id = result.get('frame_id')
    jpg_base64 = result.get('jpg_base64')
    if frame_id and jpg_base64:
        image_data = base64.b64decode(jpg_base64)
        save_path = os.path.join(save_dir, f'{frame_id}.jpg')
        with open(save_path, 'wb') as f:
            f.write(image_data)
