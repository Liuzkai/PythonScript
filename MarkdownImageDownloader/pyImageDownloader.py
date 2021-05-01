"""
识别文件下的MD文件，并将MD文件中的图片下载到本地，同时替换MD文件的图片引用路径到本地
"""

import os
import os.path
import threading
import urllib.request
from tkinter import *
from tkinter import filedialog
import re


class Article:

    def __init__(self, path):
        self.article_path = path
        self.article_pic_dir = path.replace(".md", "_Image")
        self.mkdir_image_dir()
        self.pic_list = self.find_pics(self.article_path)

    def find_pics(self, article_path):
        """
        read md and find the picture path
        :param article_path:
        :return: array<str> picture path
        """
        # UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 246: illegal multibyte sequence
        # f = open(article_path, 'r')
        f = open(article_path, 'r', encoding='utf-8')
        content=f.read()
        pics = []
        results = re.findall(r"!\[(.+?)\)", content)
        index = 0
        for result in results:
            temp_pic = result.split("](")
            if len(temp_pic) == 2:
                pic = Picture(temp_pic[0], temp_pic[1], self.article_pic_dir, index)
                pics.append(pic)
            index += 1
        f.close()
        return pics

    def mkdir_image_dir(self):
        if not os.path.exists(self.article_pic_dir):
            os.mkdir(self.article_pic_dir)

    def replace_pics_url(self):
        f = open(self.article_path, 'r+',  encoding='utf-8')
        content = f.read()
        for pic in self.pic_list:
            if os.path.exists(pic.pic_path):
                content = content.replace(pic.url, pic.pic_path, -1)
        f.close()
        with open(self.article_path, 'w', encoding='utf-8') as fout:
            fout.write(content)
            fout.close()


class Picture:
    def __init__(self, name, url, dir_path, index):
        self.name = name
        self.url = url
        self.dir_path = dir_path
        self.index = index
        self.error_reason = None
        self.pic_path = self.build_pic_name()

    def start_download_pic(self, download_pic_callback):
        pic_path = self.build_pic_name()

        if os.path.exists(pic_path):
            print('pic has existed:' + self.url)
            self.error_reason = 'pic has existed:'
            download_pic_callback(self)
            return

        if not self.url.startswith("http"):
            print('pic has invalid url:' + self.url)
            self.error_reason = "pic has invalid url"
            download_pic_callback(self)
            return

        header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
            'Cookie':'AspxAutoDetectCookieSupport=1',
        }

        request = urllib.request.Request(self.url, None, header)
        try:
            response = urllib.request.urlopen(request, timeout=10)
        except Exception as error:
            print('pic cannot download:' + self.url)
            self.error_reason = str(error)
            download_pic_callback(self)
            return

        try:
            fp = open(pic_path, 'wb')
            fp.write(response.read())
            fp.close()
        except IOError as error:
            print(error)
            self.error_reason = str(error)
            download_pic_callback(self)
            return
        download_pic_callback(self)

    def build_pic_name(self):
        # 剪去图片链接后的参数
        pic_url = self.url.split("?")[0]
        urls = pic_url.split(".")
        if len(urls)>1 :
            pic_type = urls[-1]
        else:
            pic_type = "jpg"

        if self.name is not None and len(self.name) > 0 :
            pic_name = self.name + '.' + pic_type
        elif len(self.url.split('/')[-1].split('.')[0]) > 0:
            pic_name = self.url.split('/')[-1].split('.')[0] + '.' + pic_type
        else:
            pic_name = 'no_name' + str(self.index) + '.' + pic_type

        pic_path = os.path.join(self.dir_path, pic_name)
        return pic_path


class Directory:

    @classmethod
    def find_sub_path(cls, path):
        article_list = []
        temp_files = os.listdir(path)
        for file in temp_files:
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and os.path.splitext(full_path)[1] == '.md':
                article = Article(full_path)
                article_list.append(article)
            elif os.path.isdir(full_path):
                article_list.extend(cls.find_sub_path(full_path))
        return article_list


class MDImageDownloader:

    def __init__(self):
        self.download_error_list = []
        self.all_pic_count = 0
        self.current_pic_index = 0
        self.thread_lock = threading.Lock()
        self.search_button = None
        self.articles_list = []
        self.pic_list = []
        # UI
        self.root = Tk()
        self.root.title("MDImageDownloader")
        self.path = StringVar()
        self.title = StringVar()
        self.title.set("请选择Markdown文件所在文件夹")
        self.list_box = None
        Label(self.root, textvariable = self.title).grid(row=0, column=1)
        Label(self.root, text="文件夹路径:").grid(row=1, column=0)
        Entry(self.root, textvariable=self.path).grid(row=1, column=1)
        Button(self.root, text="选择路径", command=self.select_path).grid(row=1, column=2)
        self.root.mainloop()

    def select_path(self):
        self.path.set(filedialog.askdirectory())
        if self.path.get() != '':
            self.search_button = Button(self.root, text='开始搜索并下载', command=self.start_search_dir)
            self.search_button.grid(row=2, column=1)
            return self.path

    def start_search_dir(self):
        # initialization
        self.articles_list = []
        self.pic_list = []
        self.all_pic_count = 0
        self.current_pic_index = 0
        self.download_error_list = []
        # UI changed
        self.search_button['state'] = DISABLED
        self.search_button['text'] = '正在下载...'
        self.articles_list = Directory.find_sub_path(self.path.get())
        for article in self.articles_list:
            self.pic_list.extend(article.pic_list)
        self.all_pic_count = len(self.pic_list)
        self.change_title(self.all_pic_count, self.current_pic_index)
        for pic in self.pic_list:
            thread = threading.Thread(target=pic.start_download_pic, args=(self.download_pic_callback,))
            thread.start()

    def download_pic_callback(self, pic):
        # 获取线程锁
        self.thread_lock.acquire()

        if pic.error_reason is not None and len(pic.error_reason) > 0:
            self.download_error_list.append(pic)

        self.current_pic_index += 1

        print('finish:{}/{}'.format(self.current_pic_index, self.all_pic_count))
        self.change_title(self.current_pic_index, self.all_pic_count)

        # FINISHED
        if self.all_pic_count == self.current_pic_index:
            self.search_button['text'] = "下载完成"
            self.print_error(self.download_error_list)
            for article in self.articles_list:
                article.replace_pics_url()

        # 释放锁
        self.thread_lock.release()

    def change_title(self, current_num, total_num):
        self.title.set("已经完成:{}/{}".format(current_num, total_num))

    def print_error(self, download_error_list):
        print("----------------------------------------")
        print("some pic download failure:")
        for pic in download_error_list:
            print("")
            print("name:{}".format(pic.name))
            print("url:{}".format(pic.url))
            print("error_reason:{}".format(pic.error_reason))

        Label(self.root, text="部分图片下载失败:").grid(row=4, column=1)

        self.list_box = Listbox(self.root)
        for pic in download_error_list:
            self.list_box.insert(END, pic.url + '->' + pic.error_reason)
        self.list_box.grid(row=5, column=0, columnspan=3, sticky=W+E+N+S)

        # 垂直 scrollbar
        scr1 = Scrollbar(self.root)
        self.list_box.configure(yscrollcommand=scr1.set)
        scr1['command'] = self.list_box.yview
        scr1.grid(row=5, column=4, sticky=W+E+N+S)
        # 水平 scrollbar
        scr2 = Scrollbar(self.root, orient='horizontal')
        self.list_box.configure(xscrollcommand=scr2.set)
        scr2['command'] = self.list_box.xview
        scr2.grid(row=6, column=0, columnspan=3, sticky=W+E+N+S)


dir_picker = MDImageDownloader()