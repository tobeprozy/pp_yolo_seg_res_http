import requests
import json

url = "http://172.21.2.85:5003/create"

#payload = json.dumps({"video_pt": 'rtsp://172.25.4.45:8554/mystream'})
payload = json.dumps({"dataset_pt": '/data/',"bmodel":'fp32'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
