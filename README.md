# FetchRVData

  这是一个实现了对RouteViews项目和RIPERIS项目收集到的全球路由信息数据进行下载的命令行工具,使用Python语言进行编写
  
  其中包括的主要参数有：
  
  -P: --project             type=str      #必选参数，用来选择项目，如RouteViews或RIPERIS
  
  -c: --collector           type=str      #必选参数，用来选择收集器
  
  -t: --type                type=str      #必选参数，用来确定路由信息类型，如RIBS、UPDATES、latest-update、latest-bview、updates
  
  -d: --datetime            type=str      #必选参数，用来确定路由信息的收集时间
  
  -p: --downloadpath        type=str      #可选参数，用来确定文件下载路径，默认值为'./BGPInfos'
  
  -n: --number              type=int      #可选参数，用来确定线程个数，默认值为1
  
  --proxy:                  type=str      #可选参数,用来配置代理
  
  命令使用举例：
  
  exampe1:
  
  route@ubuntu:~/PycharmProjects/FetchRVData$ python3 BGPfetcher.py -P RIPERIS -c rrc00 -t latest-update -d 202204180800 
  
  example2:
  
  route@ubuntu:~/PycharmProjects/FetchRVData$ python3 BGPfetcher.py -P RouteViews -c route-views2 -t RIBS -d 202204110800 -n 20 

# 关于Route-Views项目数据收集的一些注意事项：
  
  Route-Views中包含的收集器有：
  
  route-views2;
  
  route-views3;
  
  route-views4;
  
  route-views5;
  
  route-views6;
  
  route-views.amsix;
  
  route-views.chicago;
  
  route-views.chile;
  
  route-views.eqix;
  
  route-views.flix;
  
  route-views.gorex;
  
  route-views.isc;
  
  route-views.kixp;
  
  route-views.jinx;
  
  route-views.linx;
  
  route-views.napafrica;
  
  route-views.nwax;
  
  route-views.phoix;
  
  route-views.telxatl;
  
  route-views.wide;
  
  route-views.sydney;
  
  route-views.saopaulo;
  
  route-views2.saopaulo;
  
  route-views.sg;
  
  route-views.perth;
  
  route-views.peru;
  
  route-views.sfmix;
  
  route-views.siex;
  
  route-views.soxrs;
  
  route-views.mwix;
  
  route-views.rio;
  
  route-views.fortaleza;
  
  route-views.gixa;
  
  route-views.bdix;
  
  route-views.bknix;
  
  route-views.uaeix;
  
  route-views.ny
  
  其中的‘RIBS’信息每2小时更新一次，‘UPDATES’信息大致每15分钟更新一次（对于某些收集器来说可能在15分钟上下波动，不一定是15分钟整）
  
  # 关于RIPERIS项目收集数据的一些注意事项：
  
  RIPERIS的收集器都是以‘rrc’开头，从00开始一直到26进行编号，例如‘rrc00’,‘rrc01’等
  
  RIPERIS中提供了‘latest-update’和‘latest-bview’，即最新的更新信息和最新的BGP信息。这2者在每个月都是唯一的。
  
  若想查询指定时间段的BGP信息更新，可以查询‘updates’，该数据每5分钟更新一次
  
  RIPERIS并不提供指定时间段的全局BGP信息，只提供最新的
  
  
  
  
  
  
  
  
