import requests
import json

url = "http://172.24.12.34:5001/create"

#payload = json.dumps({"video_pt": 'rtsp://172.24.12.28:8554/mystream',"bmodel":'int8'})
#payload = json.dumps({"video_pt": 'rtmp://172.24.12.28:1935/mystream',"bmodel":'int8'})
#payload = json.dumps({"video_pt": '/home/yolov5_http/input/video_h265_1080p.mp4',"bmodel":'int8'})
#payload = json.dumps({"video_pt": 'https://nm3oss.xstore.ctyun.cn/ai_test_img/%E6%9C%AA%E6%9D%A5%E7%89%A9%E8%81%94%E7%BD%91/sample_1080p_h265.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ZY1MRAPZUFB2JXGIJAAN%2F20230724%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230724T081403Z&X-Amz-Expires=604800&X-Amz-Signature=fd8b61a429eba3d47a80fa0f4026fa7e0af801680e4051972e8075f295f529ef&X-Amz-SignedHeaders=host',"bmodel":'int8'})
#payload = json.dumps({"bmodel":'fp32'})
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
