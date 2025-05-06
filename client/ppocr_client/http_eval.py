import requests
import json

url = "http://172.21.2.85:5000/eval"

#payload = json.dumps({"video_pt": 'rtsp://172.25.4.45:8554/mystream'})
payload = json.dumps({"bmodel":'fp32'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
response_text = response.text
response_data = json.loads(response_text)
formatted_output = response_data['output'].replace(r'\n', '\n')
print(formatted_output)
