import os
import os.path
import re
import urllib
from tkinter import *
from tkinter import filedialog
import threading


class Article:

    def __init__(self, path):
        self.article_path = path
        self.article_pic_dir = path.replace(".md", "_Image")
        self.mkdir_image_dir()
        self.pic_list = self.find_pics(self.article_path)

    def find_pics(self, article_path):
        '''
        read md and find the picture path
        :param article_path:
        :return: array<str> picture path
        '''
        # UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 246: illegal multibyte sequence
        # f = open(article_path, 'r')
        f = open(article_path, 'r', encoding='utf-8')
        content = f.read()
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


class Picture:

    def __init__(self, name, url, dir_path, index):
        self.name = name
        self.url = url
        self.dir_path = dir_path
        self.index = index
        self.error_reason = None

    def start_download_pic(self, download_pic_callback):
        pic_path = self.build_pic_name()

        if os.path.exists(pic_path):
            print('pic has existed:' + self.url)
            self.error_reason = 'pic has existed:'
            download_pic_callback(self)
            return

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
        else:
            pic_name = 'no_name_' + str(self.index) + '.' + pic_type

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
        self.search_button['state'] = DISABLED
        self.search_button['text'] = '正在下载...'

        self.all_pic_count = 0
        self.current_pic_index = 0
        self.download_error_list = []
        article_list = Directory.find_sub_path(self.path.get())

    def download_pic_callback(self):
        pass

    def change_title(self):
        pass

    def print_error(self):
        pass


dir_picker = MDImageDownloader()