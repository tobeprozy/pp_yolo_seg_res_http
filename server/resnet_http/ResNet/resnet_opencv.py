#===----------------------------------------------------------------------===#
#
# Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
#
# SOPHON-DEMO is licensed under the 2-Clause BSD License except for the
# third-party components.
#
#===----------------------------------------------------------------------===#
# -*- coding: utf-8 -*- 
import os
import time
import json
import cv2
import numpy as np
import argparse
import glob
import sophon.sail as sail
import logging
logging.basicConfig(level=logging.INFO)
from queue import Queue
import base64


class Resnet(object):
    def __init__(self, bmodel, dev_id):
        # load bmodel
        self.net = sail.Engine(bmodel, dev_id, sail.IOMode.SYSIO)
        self.graph_name = self.net.get_graph_names()[0]
        self.input_names = self.net.get_input_names(self.graph_name)
        self.input_shapes = [self.net.get_input_shape(self.graph_name, name) for name in self.input_names]
        self.output_names = self.net.get_output_names(self.graph_name)
        self.output_shapes = [self.net.get_output_shape(self.graph_name, name) for name in self.output_names]
        logging.debug("load {} success!".format(bmodel))
        logging.debug(str(("graph_name: {}, input_names & input_shapes: ".format(self.graph_name), self.input_names, self.input_shapes)))
        logging.debug(str(("graph_name: {}, output_names & output_shapes: ".format(self.graph_name), self.output_names, self.output_shapes)))
        self.input_name = self.input_names[0]
        self.input_shape = self.input_shapes[0]

        self.batch_size = self.input_shape[0]
        self.net_h = self.input_shape[2]
        self.net_w = self.input_shape[3]
        
        self.mean=[0.485, 0.456, 0.406]
        self.std=[0.229, 0.224, 0.225]

        self.preprocess_time = 0.0
        self.inference_time = 0.0
        self.postprocess_time = 0.0

        self.handle = self.net.get_handle()
        self.bmcv = sail.Bmcv(self.handle)
        self.input_dtype = self.net.get_input_dtype(self.graph_name, self.input_name)
        self.output_dtype = self.net.get_output_dtype(self.graph_name, self.output_names[0])
        self.img_dtype = self.bmcv.get_bm_image_data_format(self.input_dtype)

    def preprocess(self, img):
        h, w, _ = img.shape
        if h != self.net_h or w != self.net_w:
            img = cv2.resize(img, (self.net_w, self.net_h))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype('float32')
        img = (img/255-self.mean)/self.std
        img = np.transpose(img, (2, 0, 1))
        return img

    def predict(self, input_img):
        input_data = {self.input_name: input_img}
        outputs = self.net.process(self.graph_name, input_data)
        return list(outputs.values())[0]

    def postprocess(self, outputs):
        res = list()
        outputs_exp = np.exp(outputs)
        outputs = outputs_exp / np.sum(outputs_exp, axis=1)[:,None]
        predictions = np.argmax(outputs, axis = 1)
        for pred, output in zip(predictions, outputs):
            score = output[pred]
            res.append((pred.tolist(),float(score)))
        return res

    def __call__(self, img_list):
        img_num = len(img_list)
        img_input_list = []
        for img in img_list:
            start_time = time.time()
            img = self.preprocess(img)
            self.preprocess_time += time.time() - start_time
            img_input_list.append(img)
        
        if img_num == self.batch_size:
            input_img = np.stack(img_input_list)
            start_time = time.time()
            outputs = self.predict(input_img)
            self.inference_time += time.time() - start_time
        else:
            input_img = np.zeros(self.input_shape, dtype='float32')
            input_img[:img_num] = np.stack(img_input_list)
            start_time = time.time()
            outputs = self.predict(input_img)[:img_num]
            self.inference_time += time.time() - start_time
        
        start_time = time.time()
        res = self.postprocess(outputs)
        self.postprocess_time += time.time() - start_time

        return res

    def get_time(self):
        return self.dt
        
def put_element(queue, element):
    if queue.qsize() >= 10:
        queue.get()  # 如果队列已满，移除最早放入的元素
    queue.put(element)  # 向队列中放入新元素      

my_queue = Queue(maxsize=10)

###############################################        
def create_task(bmodel, dev_id):
    values_list = []

    # 打开文本文件并逐行读取内容
    with open('./ResNet/id-label.txt', 'r') as file:
        for line in file:
            # 提取每行中的value，以空格为分隔符，去掉id部分（第一个单词）
            value = ' '.join(line.strip().split(' ')[1:])
            # 将提取到的value添加到列表中
            values_list.append(value)
    # check if model exist
    if not os.path.exists(bmodel):
        raise FileNotFoundError('{} is not existed.'.format(bmodel))
    output_dir = "./results"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    input_pt = './input/imagenet_val_1k/img'
    if not os.path.isdir(input_pt):
        # logging.error("input must be an image directory.")
        # return 0
        raise Exception('{} is not a directory.'.format(input_pt))
        
    resnet = Resnet(bmodel, dev_id)
    batch_size = resnet.batch_size
    
    img_list = []
    filename_list = []
    results_list = []
    res_dict = {}
    decode_time = 0.0
    
    for filename in glob.glob(input_pt+'/*'):
        if os.path.splitext(filename)[-1] not in ['.jpg','.png','.jpeg','.bmp','.JPEG','.JPG','.BMP']:
            continue
        start_time = time.time()
        src_img = cv2.imread(filename)
        if src_img is None:
            logging.error("{} imread is None.".format(filename))
            continue
        decode_time += time.time() - start_time
        img_list.append(src_img)
        filename_list.append(filename)
        if len(img_list) == batch_size:
            results = resnet(img_list)
            for i, filename in enumerate(filename_list):
                res_dict = dict()
                logging.info("filename: {}, res: {}".format(filename, results[i]))
                _, encoded_image  = cv2.imencode('.jpg', img_list[i])
                base64_image = base64.b64encode(encoded_image).decode('utf-8')
                put_element(my_queue, [values_list[results[i][0]], results[i][0], base64_image])
                
                res_dict['filename'] = filename
                res_dict['prediction'] = results[i][0]
                res_dict['score'] = results[i][1]
                results_list.append(res_dict)
            img_list = []
            filename_list = []
    if len(img_list):
        results = resnet(img_list)
        for i, filename in enumerate(filename_list):
            res_dict = dict()
            logging.info("filename: {}, res: {}".format(filename, results[i]))
            _, encoded_image  = cv2.imencode('.jpg', img_list[i])
            base64_image = base64.b64encode(encoded_image).decode('utf-8')
            put_element(my_queue, [values_list[results[i][0]], results[i][0], base64_image])
            
            logging.info("filename: {}, res: {}".format(filename, results[i]))
            res_dict['filename'] = filename
            res_dict['prediction'] = results[i][0]
            res_dict['score'] = results[i][1]
            results_list.append(res_dict)

    # save result
    if input_pt[-1] == '/':
        input_pt = input_pt[:-1]
    json_name = os.path.split(bmodel)[-1] + "_" + os.path.split(input_pt)[-1] + "_opencv" + "_python_result.json"
    with open(os.path.join(output_dir, json_name), 'w') as jf:
        # json.dump(results_list, jf)
        json.dump(results_list, jf, indent=4, ensure_ascii=False)
    logging.info("result saved in {}".format(os.path.join(output_dir, json_name)))
###########################################################
def get_result():
    data = []
    while not my_queue.empty():
        element = my_queue.get()
        result = {}
        result['class_name'] = element[0]
        result['class_id'] = element[1]
        result['jpg_base64'] = element[-1]
        data.append(result)
    return data

