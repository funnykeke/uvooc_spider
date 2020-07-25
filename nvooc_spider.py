import requests
import os
from queue import Queue
from urllib.parse import unquote
from lxml import etree

# 存放所有需要下载的文件的链接
file_urls_queue = Queue(maxsize=1000)
# 存放所有文件夹链接
dic_urls_queue = Queue(maxsize=1000)


# 用于创建文件夹
def makedir(path):
    os.makedirs(path)


# 用于下载文件
def download(file_url):
    file_url = str(file_url)
    file_url = 'https://pan.uvooc.com' + file_url
    file_name_list = file_url.split("CET6/")[1].split("/")
    if '' in file_name_list:
        file_name_list.remove('')
    file_name = ''
    for i in file_name_list:
        file_name = file_name + unquote(i) + '/'
    file_name = file_name[:-1]
    print("正在下载" + file_name)
    if file_url.find('.mp3') >= 0:
        try:
            r = requests.get(file_url, stream=True)
            with open(file_name, 'wb+') as m:
                m.write(r.content)
        except Exception as e:
            print('Downloading error:{}\nfile_url:{}'.format(e, file_url))
    else:
        try:
            r = requests.get(file_url)
            with open(file_name, 'wb+') as f:
                f.write(r.content)
        except Exception as e:
            print('Downloading error:{}\nfile_url:{}'.format(e, file_url))


# 访问文件夹
def get_detail(dic_url):
    if dic_url == '/Learn/CET/CET6/%E6%97%A7%E7%BD%91%E7%AB%99%E7%9C%9F%E9%A2%98%E5%A4%87%E4%BB%BD/':
        return
    global file_urls_queue
    global dic_urls_queue
    dic_url = "https://pan.uvooc.com" + dic_url
    try:
        print("访问" + dic_url)
        html = etree.HTML(requests.get(dic_url).text)
        dic_urls_temp_list = html.xpath("//li[@class='mdui-list-item mdui-ripple']/a/@href")
        # 删除返回上一页的链接
        dic_urls_temp_list.remove(dic_urls_temp_list[0])
        # 将文件夹链接存入文件夹队列并创建本地文件夹
        for i in dic_urls_temp_list:
            dic_urls_queue.put(i)
            dic_name_list = i.split("CET6/")[1].split("/")
            if '' in dic_name_list:
                dic_name_list.remove('')
            path = ''
            for x in dic_name_list:
                path = path + unquote(x) + '/'
            makedir(path)
        file_urls_temp_list = html.xpath("//li[@class='mdui-list-item file mdui-ripple']/a/@href")
        # 将文件链接存入文件队列
        for i in file_urls_temp_list:
            file_urls_queue.put(i)
    except Exception as e:
        print('web requests url error: {}\nfile_url: {}'.format(e, dic_url))


def dicrun():
    while not dic_urls_queue.empty():
        get_detail(str(dic_urls_queue.get()))


def filerun():
    while not file_urls_queue.empty():
        download(file_urls_queue.get())


if __name__ == '__main__':
    dic_urls_queue.put("/Learn/CET/CET6/")
    dicrun()
    filerun()
