#!/bin/bash
x_value="${1:-yolov5_test}"
y_value="${2:-yolov5_rtsp}"

docker run --restart always --network=host  --privileged -v /dev:/dev -td --name "$x_value" "$y_value" bash
