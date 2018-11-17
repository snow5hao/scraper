# coding=utf-8
from urllib import request,error,robotparser
import itertools
import re

#主要实现几个功能, 代理,递归查找link,符合robots,深度,
url='http://example.webscraping.com/sitemap.xml'

def download(url,user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',retryNumber=2):
    #设置代理(寻找代理http://www.xicidaili.com/)
    #后期添加可以自动查找可用代理的功能
    proxyHandler=request.ProxyHandler({'https':'27.17.45.90:43411'})
    opener=request.build_opener(proxyHandler)

    print("download:",url)
    req=request.Request(url)
    req.add_header('User-Agent',user_agent)
    try:
        reg = opener.open(req)
        return reg.read().decode('utf-8')
    except error.HTTPError as e:
            if hasattr(e,'code') and 500<=e.code<600:
                if retryNumber > 0:
                    print("%s occur, Retrying %s ....." % (e.code, retryNumber))
                    return download(url,retryNumber-1)
            else:
                print("%s error occur" % e.code)

def getLink(html):
    webpage_regex=re.compile('<a[^>]+href=["\'](http\:\/\/www\.linxueyu.*?)["\']',re.IGNORECASE)
    return webpage_regex.findall(html)

def link_crawler(FirstUrl,user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',max_depth=2,link_regex=1):
    crawl_queue=[FirstUrl]
    seen={FirstUrl:0}

    while crawl_queue:
        url=crawl_queue.pop()
        rp=get_robots(url)
        if not rp.can_fetch(user_agent,url):
            html=download(url)
            depth=seen[url]
            #检查这一个url的当前深度,如果到达当前url经历了超过深度的链接数,则不再爬取
            if depth!=max_depth:
                for link in getLink(html):
                    if link == FirstUrl:
                        continue
                    if link not in seen:
                        seen[link] = depth + 1
                        crawl_queue.append(link)
        else:
            print('Block by robots.txt')
    for i in seen:
        print(i)

#检查是否符合robots.txt配置
def get_robots(url):
    rp=robotparser.RobotFileParser()
    url=request.urljoin(url, '/robots.txt')
    rp.set_url(url)
    rp.read()
    return rp

link_crawler('http://www.linxueyu.com/')
# for page in itertools.count(1):
#     url = 'http://example.webscraping.com/view/%d' % page
#     reg=download(url)
#     if reg==None:
#         break
#     else:
#         pass
