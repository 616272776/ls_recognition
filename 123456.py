import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from paddleocr import PaddleOCR
from PIL import Image
import requests



class MyEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    # 新建
    def on_created(self, event):
        if event.is_directory:
            print("目录 created:{file_path}".format(file_path=event.src_path))
        else:
            print("{file_path}".format(file_path=event.src_path))
        b = event.src_path



        img = Image.open(b)
        print()
        # 图片尺寸
        img_size = img.size
        h = img_size[1]  # 图片高度
        print(h)
        w = img_size[0]  # 图片宽度
        print(w)
        # 设置左上角的为起始点，起始点坐标，然后设置长，宽，（通过屏幕图片得知该信息。）
        data_1 = [778, 28, 48, 17]
        x = int(data_1[0])
        y = int(data_1[1])
        w = int(data_1[2])
        h = int(data_1[3])
        # 开始截取
        region = img.crop((x, y, x + w, y + h))
        # 保存图片
        region.save("D:\\1111.png")  # 保存图片路径自行设置。




        ocr = PaddleOCR(use_angle_cls=True,
                        use_gpu=False)  # need to run only once to download and load model into memory
        img_path = "D:\\1111.png"
        result = ocr.ocr(img_path, cls=True)
        print(result)
        for line in result:
            for i in range(len(line)):
                print(line[len(line) - (i + 1)][1][0])

        # response = requests.post(url="http://8084.free.svipss.top/test", data=line[len(line) - (i + 1)][1][0])
        # print(response.text)
        # return response.status_code



if __name__ == '__main__':
    path = "C:\\Users\\11415\\Desktop\\producingProcessMonitorCapture\\2022-11-17"

    myEventHandler = MyEventHandler()

    # 观察者
    observer = Observer()

    # recursive:True 递归的检测文件夹下所有文件变化。
    observer.schedule(myEventHandler, path, recursive=True)

    # 观察线程，非阻塞式的。
    observer.start()


    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()






