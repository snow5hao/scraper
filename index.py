# coding=utf-8
from urllib import request,error,robotparser
import itertools
import re
import random
import config
from bs4 import BeautifulSoup
from lxml import etree
from chardet import detect

def getProxy(url,charset="utf-8"):
    req = request.Request(url)
    req.add_header('User-agent',random.choice(config.USER_AGENTS))
    content = request.urlopen(req).read().decode(charset,'ignore')
    soup = BeautifulSoup(content, "html.parser")
    odd=soup.find_all("tr",class_='odd')
    allProxy={}
    for i in odd:
        try:
            anonymous=i.find(text=re.compile('高匿'))
            if anonymous:
                protocol = i.find(text=re.compile('(HTTP)|(socks4/5)'))
                ip=i.find(text=re.compile('\d*\.\d*\.\d*\.\d*'))
                port=i.find(text=re.compile('^\d{2,5}$'))
                address=str(ip)+":"+str(port)
                allProxy[address]=protocol
        except:
            pass
    return allProxy

allProxy=getProxy('http://www.xicidaili.com/')

def download(url,user_agent=random.choice(config.USER_AGENTS),retryNumber=config.RETRY_TIME):
    #设置代理(寻找代理http://www.xicidaili.com/)
    #后期添加可以自动查找可用代理的功能
    proxy=random.choice(list(allProxy)) #随机挑一个代理
    proxyHandler=request.ProxyHandler({allProxy[proxy]:proxy})
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

def link_crawler(FirstUrl,user_agent=random.choice(config.USER_AGENTS),max_depth=config.MAX_DEPTH):
    crawl_queue=[FirstUrl]
    seen={FirstUrl:0}

    while crawl_queue:
        url=crawl_queue.pop()
        rp=get_robots(url)
        if rp.can_fetch(user_agent,url):
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

#检查是否符合robots.txt配置
def get_robots(url):
    rp=robotparser.RobotFileParser()
    url=request.urljoin(url, '/robots.txt')
    rp.set_url(url)
    rp.read()
    return rp

link_crawler('http://47.106.250.71/')
