# FetchRVData

  这是一个实现了对RouteViews项目和RIPERIS项目收集到的全球路由信息数据进行下载的命令行工具,使用Python语言进行编写
  
  其中包括的主要参数有：
  
  -P: --project             type=str      #必选参数，用来选择项目，如RouteViews或RIPERIS
  
  -c: --collector           type=str      #必选参数，用来选择收集器
  
  -t: --type                type=str      #必选参数，用来确定路由信息类型，如RIBS或UPDATES
  
  -d: --datetime            type=str      #必选参数，用来确定路由信息的收集时间
  
  -p: --downloadpath        type=str      #可选参数，用来确定文件下载路径，默认值为'./BGPInfos'
  
  -n: --number              type=int      #可选参数，用来确定线程个数，默认值为1
  
  --proxy:                  type=str      #可选参数,用来配置代理
  
  命令使用举例：
  
  exampe1:
  
  route@ubuntu:~/PycharmProjects/FetchRVData$ python3 BGPfetcher.py -P RIPERIS -c rrc00 -t latest-update -d 202204180800 -X
  
  example2:
  
  route@ubuntu:~/PycharmProjects/FetchRVData$ python3 BGPfetcher.py -P RouteViews -c route-views2 -t RIBS -d 202204110800 -n 20 -X -p /home/route/Documents

