import requests
import json

url = "http://172.21.2.85:5000/create"

#payload = json.dumps({"video_pt": 'rtsp://172.25.4.45:8554/mystream'})
payload = json.dumps({"dataset_pt": '/data/ppocr_http/train_full_images_0',"bmodel":'fp32'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
