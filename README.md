# FetchRVData

这是一个实现了对俄勒冈大学route-views项目收集到的全球路由信息数据进行下载的命令行工具
使用Python语言进行编写

其中包括的主要参数有：
-c: --collector           type=str      #必选参数，用来选择收集器
-t: --type                type=str      #必选参数，用来确定路由信息类型，如RIBS或UPDATES
-d: --datetime            type=str      #必选参数，用来确定路由信息的收集时间
-p: --downloadpath        type=str      #可选参数，用来确定文件下载路径，默认值为'/home/route/Documents/python-download'
-M: ----multiplethread                  #与'-S'互为互斥参数，用来开启多线程下载
-n: --number              type=int      #可选参数，用来确定线程个数，默认值为20
-S: --singlethread                      #与'-M'互为互斥参数，用来开启单线程下载
-X: --notconfigproxy                    #与'-Y'互为互斥参数，作用是不配置proxy代理
-Y: --configproxy                       #与'-X'互为互斥参数，作用是配置proxy代理

其中proxy代理的配置在configproxies.py文件中进行配置

命令使用举例：

exampe1:
route@ubuntu:~/PycharmProjects/FetchRVData$ python3 main.py -c route-views2 -t RIBS -d 202204110800 -M -n 20 -X
example2:
route@ubuntu:~/PycharmProjects/FetchRVData$ python3 main.py -c route-views2 -t RIBS -p /home/route/Documents -d 202204110800 -M -n 20 -X
