
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import sys


class MyEventHandler(FileSystemEventHandler):
    def __init__(self,url,stage,deviceId):
        FileSystemEventHandler.__init__(self)
        self.url=url
        self.stage = stage
        self.deviceId = deviceId

    # 新建
    def on_created(self, event):
        if event.is_directory:
            print("目录 created:{file_path}".format(file_path=event.src_path))
        else:
            print("{file_path}".format(file_path=event.src_path))
        files = {"files": open(event.src_path, 'rb')}

        print("上传阶段"+self.stage+" 设备id:"+self.deviceId+"的数据")
        response = requests.post(url=self.url, files=files,data={"stage":self.stage,"deviceId":self.deviceId})
        print(response.text)
        return "response.status_code"



if __name__ == '__main__':
    path = "C:\\producingProcessMonitorCapture"
    url="http://192.168.219.2:28098/MupUpload"
    stage="默认环节"
    deviceId="0001"

    # 判断运行参数，源文件目录，切割json配置目录，切割缓存目录
    if len(sys.argv) == 3:
        path = sys.argv[1]
        url = sys.argv[2]
        stage=sys.argv[3]
        deviceId = sys.argv[4]

    myEventHandler = MyEventHandler(url,stage,deviceId)

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






