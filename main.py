

#这是一个用于实时下载解析格式化导出route-views中路由数据的python工具，code by ghy

#参考了https: // blog.csdn.net / u012424313 / article / details / 82222188
#和 https://blog.csdn.net/gyuan_/article/details/120561943

#此代码需要在Ubuntu操作系统中运行
#需要安装bzip2、zlib以及bgpdump
#安装过程请参考：https://blog.csdn.net/weixin_44281841/article/details/111558527

import datetime
import requests
from bs4 import BeautifulSoup
import os
import urllib
import bz2
from urllib.request import urlretrieve


def rpthook(a,b,c):
    '''''回调函数
    @a:已经下载的数据块
    @b:数据块的大小
    @c:远程文件的大小
    '''
    per=100.0*a*b/c
    if per>100:
        per=100
    print('%.2f%%' % per)

#根据当前时间下载最新数据
def create_download_url():
    # 链接格式是"http://archive.routeviews.org/bgpdata/"+year+"."+month+"/RIBS/"于是需要根据当前的年月计算父链接
    i = datetime.datetime.now()
    year = str(i.year)
    month = str(i.month)
    day = str(i.day)
    if i.month < 10:
        month = '0'+month
    if i.day <10:
        day = '0'+day
    fatherurl = "http://archive.routeviews.org/bgpdata/"+year+"."+month+"/RIBS/"

    #通过beautifulsoup查找到倒数第二个tr标签，其中即为最新的文件
    v_response = requests.get(fatherurl)
    bs = BeautifulSoup(v_response.text, 'lxml')
    latest_file_name = bs.find_all('tr')[-2].find_next('a').text

    #生成下载链接
    url = "http://archive.routeviews.org/bgpdata/"+year+"."+month+"/RIBS/"+latest_file_name
    return url

if __name__=='__main__':
    #生成下载链接
    download_url = create_download_url()

    #指定下载地址
    download_path = input("输入指定地址，例如：/home/route/Documents/python-download/")
    download_file_path = download_path+"ribs.bz2"  #实验时地址为'/home/route/Documents/python-download/ribs.bz2'

    #下载到指定地址
    print("downloading from" + download_url + "...")
    urllib.request.urlretrieve(download_url, download_file_path,rpthook)
    print("download successful!")

    #解压缩
    f = download_file_path
    #打开压缩文件
    zipfile = bz2.BZ2File(f)
    #读文件
    data = zipfile.read()
    #设定解压缩后文件路径
    decompress_path = download_path+'ribs'
    # 写入数据
    print("decompressing...")
    open(decompress_path, 'wb').write(data)
    print("decompression is successful!")

    #解析文件
    #执行终端bgpdump命令进行解析
    print("analyzing...")
    os.system("bgpdump '"+download_file_path+"' > '"+download_path+"ribs.txt' ")
    print("analysis is successful!")