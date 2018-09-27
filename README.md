# Scrapy爬虫

Scrapy模块的框架大致如下:

![](https://scrapy-chs.readthedocs.io/zh_CN/0.24/_images/scrapy_architecture.png)

## 组件

- Scrapy Engine
    引擎主要负责控制数据流在系统中所有组件中的流动, 并在相应动作发生时出发事件.
- 调度器(Scheduler)
    调度器从引擎接受request并将它们入队, 以便之后引擎请求它们时提供引擎
- 下载器(Downloader)
    下载器负责获取页面数据并提供给引擎, 而后提供给spider
- Spiders
    Spider是用户编写用于分析response并提取item或额外跟进的url的类. 每个spider负责处理一个特定的网站
- Item Pipeline
    Item Pipeline负责处理被spider提取出来的item. 典型的处理有清理, 验证和持久化(例如存取到数据库中)
- 下载器中间件(Downloader middlewares)
    下载器中间件是在引擎及下载器之间的特定钩子, 处理Downloader传递给引擎的response. 其提供了一个简便的机制, 通过插入自定义代码来拓展scrapy的功能.
- Spider中间件(Spider middlewares)
    Spider中间件是在引擎及Spider之间的特定钩子, 处理spider的输入和输出. 其提供了一个简便的机制, 通过插入自定义代码来拓展Scrapy功能

## 数据流的方向

Scrapy中的数据流由执行引擎控制, 其过程如下:

1. 引擎打开一个网站, 找到处理该网站的Spider并向该sipder请求第一个要爬取的url
2. 引擎从Spider中获取到第一个要爬取的url并在调度器中以Request调度
3. 引擎向调度器请求下一个要爬取的url
4. 调度器返回下一个要爬取的url给引擎, 引擎将url通过下载中间件转发给下载器
5. 一旦页面下载完毕, 下载器生成一个该页面的Response, 并通过下载中间件发送给引擎
6. 引擎从下载器中接收到Response并通过Spider中间件发送给spider处理
7. Spider处理Response并返回爬取到的Item及新的Request给引擎
8. 引擎将爬取到的Item给Item Pipeline, 将Request给调度器
9. 重复, 直到调度器中没有更多的request, 引擎关闭该网站

## 解释

Scrapy的架构是异步的, 以从调度器出发的一个事件作为整个系统的驱动, 各个部件只做自己的事情.