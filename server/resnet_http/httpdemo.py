from flask import Flask, request, Response
import logging
from ResNet.resnet_opencv import create_task, get_result
import threading
from queue import Queue
import json
from flask import jsonify
import os
import subprocess
import time
import logging
logging.basicConfig(level=logging.INFO)

# 创建Flask应用对象
app = Flask(__name__)

is_task_processing = False

@app.route('/create', methods=['POST'])
def handle_create_request():
    global is_task_processing

    # 检查是否已经有任务在处理
    if is_task_processing:
        response_data = {'message': 'Task is already being processed'}
        return response_data, 400
        
    # 获取客户端发送的JSON数据
    request_data = request.get_json()
    
    # 检查JSON数据中是否包含rtsp地址
    if 'bmodel' in request_data:
        bmodel = request_data['bmodel']
        # 创建一个线程来处理任务，并将rtsp_url传递给process_task函数
        thread = threading.Thread(target=process_task, args=(bmodel,), daemon=True)
        thread.start()
        response_data = {'message': 'Task started'}
        is_task_processing = True
        return response_data, 200
    else:
        # 如果JSON数据中没有rtsp_url，则返回错误响应
        response_data = {'error': 'Missing bmodel'}
        return response_data, 400

def process_task(bmodel):
    # 在这里执行耗时的任务
    model_pt = "./model/resnet50_"+bmodel+"_1b.bmodel"
    create_task(model_pt, 0)
    
    # 处理完成后，可以在这里执行其他操作

@app.route('/eval', methods=['POST'])
def handle_eval_request():
        
    # 获取客户端发送的JSON数据
    request_data = request.get_json()
    
    # 检查JSON数据中是否包含rtsp地址
    if 'bmodel' in request_data:
        bmodel = request_data['bmodel']
        # 创建一个线程来处理任务，并将rtsp_url传递给process_task函数
        res_name = "resnet50_"+bmodel+"_1b.bmodel_img_opencv_python_result.json"
        while True:
            result_files = os.listdir('results')
            if res_name in result_files:
              cmd = "python3 tools/eval_imagenet.py --gt_path input/imagenet_val_1k/label.txt --result_json results/" + res_name
              process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
              stdout, stderr = process.communicate()

              # 打印命令的输出信息
              
              #logging.info(stderr.decode('utf-8'))

              response_data = {'message': 'Acc eval', 'output': stderr.decode('utf-8')}
              return response_data, 200

        time.sleep(1)



@app.route('/result', methods=['POST'])
def handle_result_request():
    
    # 处理结果请求
    result = get_result()
    
    json_data = json.dumps(result)
    def generate_chunks():
        chunk_size = 4096
        for i in range(0, len(json_data), chunk_size):
            yield json_data[i:i+chunk_size]
    response = Response(generate_chunks(), content_type='application/json')
    return response

if __name__ == '__main__':
    # 设置日志记录到文件
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # 启动Flask应用，接收远程请求
    app.run(host='0.0.0.0', port=5000)
