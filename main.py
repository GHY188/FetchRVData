
#这是一个用于实时下载解析格式化导出route-views中路由数据的python工具，code by ghy

#参考了 https: // blog.csdn.net / u012424313 / article / details / 82222188
#和 https://blog.csdn.net/gyuan_/article/details/120561943
#和 https://blog.csdn.net/qq_29349715/article/details/120743829

#此代码需要在Ubuntu操作系统中运行
#需要安装bzip2、zlib以及bgpdump
#安装过程请参考：https://blog.csdn.net/weixin_44281841/article/details/111558527

#/home/route/Documents/python-download

import os
import bz2
import argparse
import time
import httpx
import configproxies
from tqdm import tqdm
from threading import Thread


#创建解析对象，作为存放参数的容器
parser = argparse.ArgumentParser(description='It is a tool for fetching bgp info')

#添加命令行参数
parser.add_argument('-c','--collector',type=str,required=True,metavar='',help='choose a collector')
parser.add_argument('-t','--type',type=str,required=True,metavar='',help='choose a info type, such as RIBS or Updates')
parser.add_argument('-p','--downloadpath',type=str,required=True,metavar='',help='assign a download path')
parser.add_argument('-d','--datetime',type=str,required=True,metavar='',help='choose download date and time')

group = parser.add_mutually_exclusive_group()
group.add_argument('-M','--multiplethread',action='store_true',help='judge whether download files with multiple threads')
group.add_argument('-S','--singlethread',action='store_true',help='judge whether download files with single threads')

parser.add_argument('-n','--threadnumber',type=int,default=20,metavar='',help='the number of threads')
parser.add_argument('-x','--configproxy',type=bool,metavar='',help='config proxy')

args = parser.parse_args()


#生成下载链接
def create_download_url(collector,year,month,day,hour,minute,type):
    father_url = ""
    son_url = ""
    if collector != "route-views2":
        father_url = "http://archive.routeviews.org/"+collector+"/bgpdata/"+year+"."+month+"/"+type+"/"
    else:
        father_url = "http://archive.routeviews.org/bgpdata/"+year+"."+month+"/"+type+"/"
    if type=="RIBS":
        son_url = "rib."+year+month+day+"."+hour+"00.bz2"
    else:
        son_url = "updates." + year + month + day + "." + hour + minute+".bz2"
    url = father_url+son_url
    return url

#下载方法
class DownloadFile(object):
    def __init__(self, download_url, data_folder, thread_num):
        """
        :param download_url: 文件下载连接
        :param data_folder: 文件存储目录
        :param thread_num: 开辟线程数量
        """
        self.download_url = download_url
        self.data_folder = data_folder
        self.thread_num = thread_num
        self.file_size = None
        self.cut_size = None
        self.tqdm_obj = None
        self.thread_list = []
        self.file_path = os.path.join(self.data_folder, download_url.split('/')[-1])

    def downloader(self, etag, thread_index, start_index, stop_index, retry=False):
        sub_path_file = "{}_{}".format(self.file_path, thread_index)
        if os.path.exists(sub_path_file):
            temp_size = os.path.getsize(sub_path_file)  # 本地已经下载的文件大小
            if not retry:
                self.tqdm_obj.update(temp_size)  # 更新下载进度条
        else:
            temp_size = 0
        if stop_index == '-': stop_index = ""
        headers = {'Range': 'bytes={}-{}'.format(start_index + temp_size, stop_index),
                   'ETag': etag, 'if-Range': etag,
                   }
        down_file = open(sub_path_file, 'ab')
        try:
            with httpx.stream("GET", self.download_url, headers=headers) as response:
                num_bytes_downloaded = response.num_bytes_downloaded
                for chunk in response.iter_bytes():
                    if chunk:
                        down_file.write(chunk)
                        self.tqdm_obj.update(response.num_bytes_downloaded - num_bytes_downloaded)
                        num_bytes_downloaded = response.num_bytes_downloaded
        except Exception as e:
            print("Thread-{}:请求超时,尝试重连\n报错信息:{}".format(thread_index, e))
            self.downloader(etag, thread_index, start_index, stop_index, retry=True)
        finally:
            down_file.close()
        return

    def get_file_size(self):
        """
        获取预下载文件大小和文件etag
        :return:
        """
        with httpx.stream("GET", self.download_url) as response2:
            etag = ''
            total_size = int(response2.headers["Content-Length"])
            for tltle in response2.headers.raw:
                if tltle[0].decode() == "ETag":
                    etag = tltle[1].decode()
                    break
        return total_size, etag

    def cutting(self):
        """
        切割成若干份
        :param file_size: 下载文件大小
        :param thread_num: 线程数量
        :return:
        """
        cut_info = {}
        cut_size = self.file_size // self.thread_num
        for num in range(1, self.thread_num + 1):
            if num != 1:
                cut_info[num] = [cut_size, cut_size * (num - 1) + 1, cut_size * num]
            else:
                cut_info[num] = [cut_size, cut_size * (num - 1), cut_size * num]
            if num == self.thread_num:
                cut_info[num][2] = '-'
        return cut_info, cut_size

    def write_file(self):
        """
        合并分段下载的文件
        :param file_path:
        :return:
        """
        if os.path.exists(self.file_path):
            if len(self.file_path) >= self.file_size:
                return
        with open(self.file_path, 'ab') as f_count:
            for thread_index in range(1, self.thread_num + 1):
                with open("{}_{}".format(self.file_path, thread_index), 'rb') as sub_write:
                    f_count.write(sub_write.read())
                # 合并完成删除子文件
                os.remove("{}_{}".format(self.file_path, thread_index))
        return

    def create_thread(self, etag, cut_info):
        """
        开辟多线程下载
        :param file_path: 文件存储路径
        :param etag: headers校验
        :param cut_info:
        :return:
        """

        for thread_index in range(1, self.thread_num + 1):
            thread = Thread(target=self.downloader,
                            args=(etag, thread_index, cut_info[thread_index][1], cut_info[thread_index][2]))

            thread.setName('Thread-{}'.format(thread_index))
            thread.setDaemon(True)
            thread.start()
            self.thread_list.append(thread)

        for thread in self.thread_list:
            thread.join()
        return

    def check_thread_status(self):
        """
        查询线程状态。
        :return:
        """
        while True:
            for thread in self.thread_list:
                thread_name = thread.getName()
                if not thread.isAlive():
                    print("{}:已停止".format(thread_name))
            time.sleep(1)

    def create_data(self):
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
        return

    def main(self):
        # 平分几份
        self.create_data()
        self.file_size, etag = self.get_file_size()
        # 按线程数量均匀切割下载文件
        cut_info, self.cut_size = self.cutting()
        # 下载文件名称
        # 创建下载进度条
        self.tqdm_obj = tqdm(total=self.file_size, unit_scale=True, desc=self.file_path.split('/')[-1],
                             unit_divisor=1024,
                             unit="B")
        # 开始多线程下载
        self.create_thread(etag, cut_info)
        # 合并多线程下载文件
        self.write_file()
        return


#解压缩
def decompress_file(download_file_path,download_path):
    f = download_file_path
    # 打开压缩文件
    zipfile = bz2.BZ2File(f)
    # 读文件
    data = zipfile.read()
    # 设定解压缩后文件路径
    decompress_path = download_path + 'ribs'
    # 写入数据
    print("decompressing...")
    open(decompress_path, 'wb').write(data)
    print("decompression is successful!")

#解析文件
def analyze_file(download_file_path,download_path):
    # 解析文件
    # 执行终端bgpdump命令进行解析
    print("analyzing...")
    os.system("bgpdump '" + download_file_path + "' > '" + download_path + "ribs.txt' ")
    print("analysis is successful!")


if __name__=='__main__':
    num = 0
    datetime = args.datetime
    file_year = datetime[0:4]
    file_month = datetime[4:6]
    file_day = datetime[6:8]
    file_hour = datetime[8:10]
    file_minute = datetime[10:12]
    #生成下载链接
    download_url = create_download_url(args.collector,file_year,file_month,file_day,file_hour,file_minute,args.type)

    #生成下载路径
    download_path = args.downloadpath
    download_file_path = download_path+"/ribs.bz2"

    #判断是否多线程下载
    if args.singlethread:
        downloader = DownloadFile(download_url, download_path, 1)
        downloader.main()
    elif args.multiplethread:
        downloader = DownloadFile(download_url, download_path, args.threadnumber)
        downloader.main()
    else:
        downloader = DownloadFile(download_url, download_path, 1)
        downloader.main()



