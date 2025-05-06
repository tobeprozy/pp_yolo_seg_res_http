# yolov5s
## server启动
1. 将yolov5s_se5_test.tar.gz下载到盒子上并解压
2. 进入yolov5s_se5_test文件夹，可以看到一个tar包与一个run_docker.sh脚本
3. 使用load命令加载镜像：docker load -i yolov5s_http.tar
4. 检查镜像是否load成功：docker images|grep yolov5s
5. 使用脚本创建container： sh run_docker.sh <自定义容器名> yolov5s
6. 进入container： docker exec -it <自定义容器名> bash
7. 运行进程：1）前台运行 python3 httpdemo.py; 2) 后台运行 sh run.sh 1;  如在输出中或output.log中看到INFO:werkzeug:Press CTRL+C to quit，则启动成功
*注意：需要留意log中端口号，例如
    * Running on all addresses (0.0.0.0)
    * Running on http://127.0.0.1:5001
    * Running on http://172.24.12.34:5001
则后续client端需将url中端口设为5001
server端端口设定在httpdemo.py中定义

## client请求
1. 将yolov5s_client.tar.gz下载到客户端并解压
2. 三个脚本均为发送http POST请求脚本 修改三个py文件中的url的ip地址:端口号为盒子的ip地址与该服务的端口（上文提及） 确保客户端服务器能连通盒子
3. 修改http_create.py中payload变量中video_pt字段的值，提供了各种案例供参考，支持本地文件、rtsp/rtmp推流、uri；bmodel字段可以修改量化模型，支持fp32与int8
4. python3 http_create.py #下发请求，盒子上的程序会开始运行
5. python3 http_result.py #获取十张结果图片，保存在同目录下img_with_results目录中
6. python3 http_eval.py #等待盒子完成推理并运行精度测试脚本，返回精度信息
*注意：不可重复create，如需再次create，请重新拉起httpdemo进程



# ppocr
1. 把ppocr_http_base.tar.gz解压到docker中。
2. cd ppocr_http
3. pip3 install python/*whl 
4. python3 http_demo.py


5. 把ppocr_client_20230720.tar.gz解压到服务器上
6. cd ppocr_client
7. 修改三个py文件中的ip地址为盒子的ip地址，确保服务器能连通盒子
8. python3 http_create.py #下发请求，盒子上的程序会开始运行
9. python3 http_result.py #获取十张结果图片，保存在同目录下img_infer_results目录中
10. python3 http_eval.py #等待盒子完成推理并运行精度测试脚本，返回精度信息。
默认测试fp32，如果测试int8，把http_create.py和http_eval.py里面的fp32换成int8即可

# segformer运行方式同ppocr
# resnet运行方式同ppocr

resnet的client可复用yolov5s的client，其中create中的video_pt字段失效
resnet的result脚本会获取最近处理的十张图片的结果并保存到当前目录下的img_with_results目录中，其中图片的文件名为图片中物体的分类名。


