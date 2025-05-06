import requests
import json

url = "http://172.24.12.34:5001/eval"


payload = json.dumps({"bmodel":'fp32'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
response_text = response.text
response_data = json.loads(response_text)
formatted_output = response_data['output'].replace(r'\n', '\n')
print(formatted_output)
