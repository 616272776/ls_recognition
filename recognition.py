import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from paddleocr import PaddleOCR
from PIL import Image
import requests
import json
import cv2 as cv
import sys
import os
import numpy as np

ocr = PaddleOCR(use_angle_cls=True, lang="ch",
                page_num=2)  # need to run only once to download and load model into memory


# 根据路径获取json对象
def getConfigJson(stageConfigPath):
    # 打开文件
    stageConfigFile = open(stageConfigPath, 'r', encoding='utf-8')
    if stageConfigFile is None:
        return False
        pass
    # 读取字符串
    stageConfigStr = stageConfigFile.read()
    # 字符串转json
    stageConfigJson = json.loads(stageConfigStr)
    return stageConfigJson


#cv图像预处理
def cv_pretreatmentAndProcessing(cutPicPath):
    #图片读取
    img = cv.imread(cutPicPath, 1)
    #预处理阶段
    img_s = img.shape  # 显示尺寸
    print(img_s)
    size = cv.resize(img, (348, 96))  # 更改尺寸
    gray = cv.cvtColor(size, cv.COLOR_BGR2GRAY)  # 灰度处理
    ret, binary = cv.threshold(gray, 120, 255, cv.THRESH_BINARY)  # 二值化
    kernel = np.ones(shape=[0, 0], dtype=np.uint8)  # 定义核结构
    eo = cv.dilate(binary, kernel, iterations=0)

    #图像加工阶段
    #处理3的
    contours3, hierarchy3 = cv.findContours(eo, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)# 图片轮廓
    cnt3 = contours3[3]
    hull3 = cv.convexHull(cnt3)
    cv.polylines(eo, [hull3], True, (255, 0, 0), 2)
    #处理4的
    contours4, hierarchy4 = cv.findContours(binary, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)  # 图片轮廓
    cnt4 = contours4[4]
    hull4 = cv.convexHull(cnt4)
    cv.polylines(eo, [hull4], True, (255, 0, 0), 2)
    #处理2的
    contours2, hierarchy2 = cv.findContours(binary, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)  # 图片轮廓
    cnt2 = contours2[2]
    hull2 = cv.convexHull(cnt2)
    cv.polylines(eo, [hull2], True, (255, 0, 0), 2)
    # #处理0的
    contours0, hierarchy0 = cv.findContours(binary, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)  # 图片轮廓
    cnt0 = contours0[0]
    # 寻找凸包并绘制凸包（轮廓）
    hull0 = cv.convexHull(cnt0)
    cv.polylines(eo, [hull0], True, (255, 0, 0), 2)
    #处理1的
    contours1, hierarchy1 = cv.findContours(binary, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)  # 图片轮廓
    cnt1 = contours1[1]
    # 寻找凸包并绘制凸包（轮廓）
    hull1 = cv.convexHull(cnt1)
    cv.polylines(eo, [hull1], True, (255, 0, 0), 2)
    return eo


# 用剪切数据剪切图片
def cutPic(img, deviceId, cutDate):
    # 图片尺寸
    img_size = img.size
    h = img_size[1]  # 图片高度
    w = img_size[0]  # 图片宽度
    cutPicFile = img.crop((float(cutDate["x"]), float(cutDate["y"]), float(cutDate["x1"]), float(cutDate["y1"])))

    # 图像处理
    cutPicFile = cv_pretreatmentAndProcessing(cutPicFile)

    path = "D:\\" + deviceId + "." + img.filename.split(".")[len(img.filename.split(".")) - 1]
    cutPicFile = cutPicFile.convert("RGB")
    cutPicFile.save(path)
    print("裁剪图片", img.filename)
    print("裁剪参数", cutDate)
    return path


# 识别图片
def recognition(cutPicPath):
    result = ocr.ocr(cutPicPath, det=False, cls=False)
    print("识别结果", result)
    return result[0][0][0]


# 发送post请求
def sendPostMessage(url, data, device):
    print(device + "向" + url + "发送数据：" + data.__str__())
    data["diviceId"] = device
    result = requests.post(url, data=data)
    print("发送结果" + result.__str__())


# 循环执行分析事件
class MyEventHandler(FileSystemEventHandler):

    def __init__(self, stage):
        FileSystemEventHandler.__init__(self)
        self.stage = stage

    # 新建
    def on_created(self, event):
        # 固晶，焊线，点胶
        deviceId = self.stage['deviceId']
        imgPath = event.src_path
        img = Image.open(imgPath, "r")

        sendData = {}

        # 循环开始剪切
        for cutDate in self.stage['cutDatas']:
            # 剪切图片
            cutPicPath = cutPic(img, self.stage['deviceId'], cutDate)
            # 识别图片内容
            recData = recognition(cutPicPath)
            # 保存内容，等发送http请求给服务器
            sendData[cutDate['key']] = recData

        sendPostMessage(self.stage['url'], sendData, self.stage['deviceId'])


# 设置观察者
def observerHandler(handler, path, seconds):
    observer = Observer()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(seconds)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':

    # 默认识别图片目录
    jsonConfigPath = "C:\\ls_config.json"

    # 判断运行参数，源文件目录，切割json配置目录，切割缓存目录
    if len(sys.argv) == 2:
        jsonConfigPath = sys.argv[1]

    # 获取json配置
    stageConfig = getConfigJson(jsonConfigPath)

    # 循环监听每个生产环节
    if stageConfig is None:
        exit()
        pass

    print("启动完成")
    for stage in stageConfig['data']:
        analysePath = stage["analysePath"]

        if os.path.exists(analysePath) is False:
            print("%s路径不存在，已创建" % analysePath)
            os.makedirs(analysePath)
        # 创建处理对象和监听对象
        myEventHandler = MyEventHandler(stage)
        observerHandler(myEventHandler, analysePath, 5)
