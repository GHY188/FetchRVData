import logging
import argparse
import options
import os
import sys
import time
from threading import Thread
import httpx
from tqdm import tqdm
# 创建解析对象，作为存放参数的容器


parser = argparse.ArgumentParser(description='It is a tool for fetching bgp info. You must assign project, collector, type and datetime.'
                                             'You can also customize downloadpath, threadnumber and proxy.')
parser.add_argument('-P', '--project', type=str, required=True, metavar='', help='*required* choose a project')
parser.add_argument('-c', '--collector', type=str, required=True, metavar='', help='*required* choose a collector')
parser.add_argument('-t', '--type', type=str, required=True, metavar='',
                    help='*required* choose a info type, such as RIBS or Updates')
parser.add_argument('-d', '--datetime', type=str, required=True, metavar='',
                    help='*required* type a 6 characters-long string contains year, month such as 202205')
parser.add_argument('-n', '--threadnumber', type=int, default=1, metavar='', help='the number of threads')
parser.add_argument('--proxy', type=str, default=None, metavar='', help='Configure the proxy for download')
parser.add_argument('-m','--more',type=str,default=None, metavar='', help='set a begin point of download set.')

args = parser.parse_args()



# 检查输入参数的合法性，不合法抛出异常
def check_args():
    # 日期长度不是6位
    if len(args.datetime) != 6:
        raise Exception("datetime format error!")
    # 项目名称输入错误
    if args.project not in options.projects:
        raise Exception("project not exist!")
    # 收集器名称输入错误
    if args.collector not in options.routeviews_collectors and args.collector not in options.ripe_collectors:
        raise Exception("collector not exist!")
    # 数据类型输入错误
    if args.type not in options.routeviews_type and args.type not in options.ripe_type:
        raise Exception("type error!")
    # 收集器名称与项目名称不匹配 ---- routeviews
    if args.project==options.projects[0] and args.collector not in options.routeviews_collectors:
        raise Exception("routeviews collector name error!")
    # 数据类型与项目名称不匹配 ---- routeviews
    if args.project == options.projects[0] and args.type not in options.routeviews_type:
        raise Exception("routeviews data type error!")
    # 收集器名称与项目名称不匹配 ---- ripe
    if args.project==options.projects[1] and args.collector not in options.ripe_collectors:
        raise Exception("ripe collector name error!")
    # 数据类型与项目名称不匹配 ---- ripe
    if args.project == options.projects[1] and args.type not in options.ripe_type:
        raise Exception("ripe data type error!")
    # 设置开头参数不合法
    if args.more:
        if args.project=="RouteViews":
            if args.type=="RIBS":
                if len(args.more)!=21:
                    raise Exception("begin point format error!")
                if args.type == "UPDATES":
                    if len(args.more) != 25:
                        raise Exception("begin point format error!")
        if args.project=="RIPERIS":
            if args.type=="updates":
                if len(args.more)!=24:
                    raise Exception("begin point format error!")
            if args.type=="bview":
                if len(args.more)!=22:
                    raise Exception("begin point format error!")

# 根据输入的参数生成下载链接集,返回一个列表
def create_urls():
    urls = []
    year = args.datetime[0:4]
    month = args.datetime[4:]
    # 判断该月份一共有几天
    if '0' == month[0]:
        month_num = int(month[-1])
    else:
        month_num = int(month)
    if month_num<=7 and month_num%2!=0:
        days = 32
    elif month_num>7 and month_num%2==0:
        days = 32
    else:
        days = 31
    collector = args.collector
    # 生成下载链接 ---- routeviews
    if args.project == options.projects[0] and args.type=='RIBS':
        if collector == 'route-views2':
            for day in range(1, days):
                for hour in range(0, 24, 2):
                    if day < 10 and hour < 10:
                        urls.append(
                            f"http://archive.routeviews.org/bgpdata/{year}.{month}/RIBS/rib.{year}{month}0{day}.0{hour}00.bz2")
                    if day < 10 and hour >= 10:
                        urls.append(
                            f"http://archive.routeviews.org/bgpdata/{year}.{month}/RIBS/rib.{year}{month}0{day}.{hour}00.bz2")
                    if day >= 10 and hour < 10:
                        urls.append(
                            f"http://archive.routeviews.org/bgpdata/{year}.{month}/RIBS/rib.{year}{month}{day}.0{hour}00.bz2")
                    if day >= 10 and hour >= 10:
                        urls.append(
                            f"http://archive.routeviews.org/bgpdata/{year}.{month}/RIBS/rib.{year}{month}{day}.{hour}00.bz2")
        else:
            for day in range(1,days):
                for hour in range(0,24,2):
                    if day<10 and hour<10:
                        urls.append(
                            f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/RIBS/rib.{year}{month}0{day}.0{hour}00.bz2")
                    if day<10 and hour>=10:
                        urls.append(
                            f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/RIBS/rib.{year}{month}0{day}.{hour}00.bz2")
                    if day>=10 and hour<10:
                        urls.append(
                            f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/RIBS/rib.{year}{month}{day}.0{hour}00.bz2")
                    if day>=10 and hour>=10:
                        urls.append(
                            f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/RIBS/rib.{year}{month}{day}.{hour}00.bz2")
    if args.project == options.projects[0] and args.type == 'UPDATES':
        if collector == 'route-views2':
            for day in range(1, days):
                for hour in range(0, 24):
                    for min in range(0,60,15):
                        if day < 10 and hour < 10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.0{hour}0{min}.bz2")
                        if day < 10 and hour >= 10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.{hour}0{min}.bz2")
                        if day >= 10 and hour < 10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.0{hour}0{min}.bz2")
                        if day >= 10 and hour >= 10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.{hour}0{min}.bz2")
                        if day < 10 and hour < 10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.0{hour}{min}.bz2")
                        if day < 10 and hour >= 10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.{hour}{min}.bz2")
                        if day >= 10 and hour < 10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.0{hour}{min}.bz2")
                        if day >= 10 and hour >= 10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.{hour}{min}.bz2")
        else:
            for day in range(1,days):
                for hour in range(0,24):
                    for min in range(0,60,15):
                        if day<10 and hour<10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.0{hour}0{min}.bz2")
                        if day<10 and hour>=10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.{hour}0{min}.bz2")
                        if day>=10 and hour<10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.0{hour}0{min}.bz2")
                        if day>=10 and hour>=10 and min<=0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.{hour}0{min}.bz2")
                        if day<10 and hour<10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.0{hour}{min}.bz2")
                        if day<10 and hour>=10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}0{day}.{hour}{min}.bz2")
                        if day>=10 and hour<10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.0{hour}{min}.bz2")
                        if day>=10 and hour>=10 and min>0:
                            urls.append(
                                f"http://archive.routeviews.org/{collector}/bgpdata/{year}.{month}/UPDATES/updates.{year}{month}{day}.{hour}{min}.bz2")

    # 生成下载链接 ---- ris
    if args.project == options.projects[1] and args.type=='updates':
        for day in range(1, days):
            for hour in range(0, 24):
                for min in range(0, 60, 5):
                    if day < 10 and hour < 10 and min<10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}0{day}.0{hour}0{min}.gz")
                    if day < 10 and hour >= 10 and min<10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}0{day}.{hour}0{min}.gz")
                    if day >= 10 and hour < 10 and min<10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}{day}.0{hour}0{min}.gz")
                    if day >= 10 and hour >= 10 and min<10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}{day}.{hour}0{min}.gz")
                    if day < 10 and hour < 10 and min>=10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}0{day}.0{hour}{min}.gz")
                    if day < 10 and hour >= 10 and min>=10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}0{day}.{hour}{min}.gz")
                    if day >= 10 and hour < 10 and min>=10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}{day}.0{hour}{min}.gz")
                    if day >= 10 and hour >= 10 and min>=10:
                        urls.append(
                            f"https://data.ris.ripe.net/{collector}/{year}.{month}/updates.{year}{month}{day}.{hour}{min}.gz")
    if args.project == options.projects[1] and args.type =='latest-update':
        urls.append(
            f"https://data.ris.ripe.net/{collector}/latest-update.gz")
    if args.project == options.projects[1] and args.type =='latest-bview':
        urls.append(
            f"https://data.ris.ripe.net/{collector}/latest-bview.gz")
    if args.project == options.projects[1] and args.type=='bview':
        for day in range(1, days):
            for hour in range(0, 23, 8):
                if day < 10 and hour < 10:
                    urls.append(
                        f"https://data.ris.ripe.net/{collector}/{year}.{month}/bview.{year}{month}0{day}.0{hour}00.gz")
                if day < 10 and hour >= 10:
                    urls.append(
                        f"https://data.ris.ripe.net/{collector}/{year}.{month}/bview.{year}{month}0{day}.{hour}00.gz")
                if day >= 10 and hour < 10:
                    urls.append(
                        f"https://data.ris.ripe.net/{collector}/{year}.{month}/bview.{year}{month}{day}.0{hour}00.gz")
                if day >= 10 and hour >= 10:
                    urls.append(
                        f"https://data.ris.ripe.net/{collector}/{year}.{month}/bview.{year}{month}{day}.{hour}00.gz")

    return urls

# 下载类
class DownloadFile(object):
    def __init__(self, download_url, thread_num):
        """
        :param download_url: 文件下载连接
        :param thread_num: 开辟线程数量
        """
        self.download_url = download_url
        self.thread_num = thread_num
        self.file_size = None
        self.cut_size = None
        self.tqdm_obj = None
        self.thread_list = []

        # 设置下载文件存放路径
        self.file_path = os.path.join('/mnt/data',args.project, args.collector, args.datetime[0:4]+'.'+args.datetime[4:6], args.type, download_url.split('/')[-1])
        self.data_folder = os.path.join('/mnt/data',args.project, args.collector, args.datetime[0:4]+'.'+args.datetime[4:6], args.type)


    def downloader(self, etag, thread_index, start_index, stop_index, retry=False, retry_time=0):
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
            with httpx.stream("GET", self.download_url, headers=headers,proxies=args.proxy) as response:
                num_bytes_downloaded = response.num_bytes_downloaded
                for chunk in response.iter_bytes():
                    if chunk:
                        down_file.write(chunk)
                        self.tqdm_obj.update(response.num_bytes_downloaded - num_bytes_downloaded)
                        num_bytes_downloaded = response.num_bytes_downloaded
        except Exception as e:
            if retry_time < 19:
                retry_time +=1
                print("Thread-{}:请求超时,第{}次重试\n报错信息:{}".format(thread_index, retry_time,e))
                self.downloader(etag, thread_index, start_index, stop_index, retry=True, retry_time=retry_time)
            elif retry_time == 19:
                retry_time += 1
                print("Thread-{}:请求超时,第{}次重试\n报错信息:{}".format(thread_index, retry_time, e))
                self.downloader(etag, thread_index, start_index, stop_index, retry=False, retry_time=retry_time)
            else:
                print('因为线程超时重试次数太多，将未完成的文件写入日志中...')
                logger = logger_config(log_path='log.txt', logging_name=self.download_url)
                logger.error("因线程超时下载未完成")
                down_file.close()
        finally:
            down_file.close()
        return

    def get_file_size(self):
        """
        获取预下载文件大小和文件etag
        :return:
        """
        with httpx.stream("HEAD", self.download_url) as response2:
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
            os.makedirs(self.data_folder)
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

# 当设置下载开头时，生成从下载开头到原下载集结尾的下载链接列表
def start_at(begin, urls):
    start_set = []
    for i in range(0,len(urls)):
        if urls[i].split('/')[-1] == begin:
            for j in range(i+1,len(urls)):
                start_set.append(urls[j])
    return start_set

def logger_config(log_path, logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出ERROR及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.ERROR)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    handler.setFormatter(formatter)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    return logger

# 运行时使用异常检测
if __name__ == '__main__':

    try:
        # 如果参数中设置了下载起始点
        if args.more:
            check_args()  # 检查参数合法性
            download_urls = create_urls() # 创建全部下载链接列表
            start_set = start_at(args.more, download_urls)  # 从下载链接列表里筛选链接生成新列表
            for url in start_set:   # 对列表里的链接逐个进行下载
                downloader = DownloadFile(url, args.threadnumber)
                downloader.main()
        else:
            check_args()
            download_urls = create_urls()
            for url in download_urls:
                downloader = DownloadFile(url,args.threadnumber)
                downloader.main()
    except Exception as err:
        print(err)