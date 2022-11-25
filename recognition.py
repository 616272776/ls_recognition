import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from paddleocr import PaddleOCR
from PIL import Image
import requests
import json
# import cv2 as cv
import sys
import os


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


# 用剪切数据剪切图片
def cutPic(img, deviceId, cutDate):
    # 图片尺寸
    img_size = img.size
    h = img_size[1]  # 图片高度
    w = img_size[0]  # 图片宽度
    cutPicFile = img.crop((float(cutDate["x"]), float(cutDate["y"]), float(cutDate["x1"]), float(cutDate["y1"])))
    path = "C:\\" + deviceId + "." + img.filename.split(".")[len(img.filename.split(".")) - 1]
    cutPicFile = cutPicFile.convert("RGB")
    cutPicFile.save(path)
    print("裁剪图片", img.filename)
    print("裁剪参数", cutDate)
    return path


ocr = PaddleOCR(use_angle_cls=True, lang="ch",
                page_num=2)  # need to run only once to download and load model into memory


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
