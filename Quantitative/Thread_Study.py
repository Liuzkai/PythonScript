import threading,time

count = 0

# 创建一个继承thread.Thread的类MyThread，并且重写run函数
class MyThread(threading.Thread):
'''
Thread是threading模块中最重要的类之一，可以使用它来创建线程。具体使用方法：创建一个threading.Thread对象，在
它的初始化函数中将需要调用的对象作为初始化参数传入。
'''
    def __init__(self,lock,threadName):
        super(MyThread,self).__init__(name=threadName)
        self.lock = lock

    def run(self):
        global count
        self.lock.acquire() #锁定当前线程
        for i in range(10):
            count=count+1
            time.sleep(0.3)
            print(self.getName(),count)
        self.lock.release() #释放当前线程

lock = threading.Lock() #锁定类
for i in range(2):
    MyThread(lock,("MyThreadName:" + str(i))).start()   # start()是启动线程的方法，run()是线程运行的内容

def doWaiting():
    print('start waiting:', time.strftime('%S'))
    time.sleep(3)
    print('stop waiting:', time.strftime('%S'))
    thread1 = threading.Thread(target = doWaiting)
    thread1.start()
    time.sleep(1)
    print('start join')
    thread1.join()
    print('end join')
# doWaiting()
