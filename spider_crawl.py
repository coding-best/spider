#!/usr/bin/env python
# -*- coding:utf-8 -*-
##############################################
#
# This spider main module 
#
############################################## 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import re
import threading
import linkquence
import configuration as cf
import logging
import log
import time
import os
import urlparse



class Spider(object):
    """docstring for Spider"""

    def __init__(self, conf):
        
        self.proxies = cf.proxies
        self.headers = cf.headers
        self.current_depth = 0
        self.pattern = str(conf['target_url']).strip()
        self.max_depth = int(conf['max_depth'])
        self.output = conf['output_directory']
        self.urls_file = conf['url_list_file']
        self.thread_count = int(conf['thread_count'])
        self.crawl_timeout = int(conf['crawl_timeout'])
        self.crawl_interval = int(conf['crawl_interval'])
        self.seeds = []
        self.threads = []
        with open (self.urls_file) as f:
            for line in f.readlines():
                line = line.strip('\n')
                self.seeds.append(line)
        logging.info("Add the seeds url \"%s\"" % self.seeds) 

    def muti_thread_crawl(self):
        """
        多线程抓取
        """
        for i in self.seeds:
            logging.info("current threads.count:%s,max threads count:%s" % (len(self.threads),self.thread_count))         
            mythread = threading.Thread(target=self.crawl, args=(i,))
            self.threads.append(mythread)
        
        logging.info("Begin Crawling")
        for t in self.threads:
            logging.info("%s is start" % t.getName())
            t.start()
            #控制线程并发的数量
            while True:
                if len(threading.enumerate()) < self.thread_count:
                    break

        for t in self.threads:
            t.join()
            logging.info("%s is done" % t.getName())
        sys.exit(0)
    
    def crawl(self, seed):
        """
        抓取函数
        """
        #根据每一个线程初始化独自的种子队列
        linksQuence = linkquence.linkQuence()
        linksQuence.addUnvisitedUrl(seed)
        #初始化抓取深度
        current_depth = 0
        #初始化空列表存放获取的urls
        urlslink = []
        while current_depth < self.max_depth:
            while not linksQuence.unVisitedUrlsEnmpy():
                visitUrl = linksQuence.unVisitedUrlDeQuence()
                if visitUrl is None or visitUrl == "":
                    continue
                logging.info("crawling the urls : %s, current_depth=%s" % (visitUrl, current_depth))
                time.sleep(1)
                html = self.get_html_content(visitUrl)
                urls = self.get_urls(html,visitUrl)
                if urls:
                    logging.info("get %s new links" % len(urls))
                    linksQuence.addVisitedUrl(visitUrl)
                    urlslink.extend(urls)
                    print urlslink
                else:
                    logging.error("the url:%s does have another url link" % visitUrl)

            for url in urlslink:
                if url != "" and url not in linksQuence.getVisitedUrl():
                    linksQuence.addUnvisitedUrl(url)
            current_depth += 1
            urlslink = []                       
        logging.info("this thread crawling done!!! max_depth=%s" % self.max_depth)
        self.print_out(linksQuence)



    def get_html_content(self, url):
        """
        获取网页内容
        """
        try:
            requests.packages.urllib3.disable_warnings()
            response = requests.get(url, headers=self.headers, verify=False, timeout=self.crawl_timeout) #, proxies=self.proxies, timeout=(3, 3))
            if response.status_code == 200:
                logging.info('get %s content successfully' % url)
                coding = response.apparent_encoding
                response.encoding = str(coding)
                return response.text
            else:
                logging.error("get url: %s faild,status_code = %s" % (url, response.status_code))
        except requests.exceptions.ConnectionError as e:
            logging.error("connect to the %s FAILD, %s" % (url, e.message))
        except requests.exceptions.ConnectTimeout as e:
            logging.error("connect to the %s FAILD, %s" % (url, e.message))
        except requests.exceptions.ProxyError as e :
            logging.error("connect to the %s FAILD, %s" % (url, e.message))        
        except Exception as e:
            logging.error("connect to the %s FAILD, %s" % (url, e.message)) 

    def get_urls(self, html, baseUrl):
        """
        获取网页内容里的url链接
        """
        #soup = BeautifulSoup(html, 'lxml')
        if html :
            url_list = re.findall(self.pattern, html, re.I)
            #处理相对路径和绝对路径
            urls = []
            for url in url_list:
                url_parse = urlparse.urlparse(url)
                url_join = urlparse.urljoin(baseUrl,url)
                #url_join = url_parse.netloc
                urls.append(url_join)
            #转换为set去重
            real_urls = list(set(urls))
            return real_urls
        else:
            return None
    
    def print_out(self,linkquence):
        """
        输出结果
        """
        vlist = linkquence.getVisitedUrl()
        nlist = linkquence.getUnvisitedUrl()
        if not os.path.isdir(self.output):
            os.makedirs(self.output)
        #打印抓取且已经访问过的链接
        with open(self.output + "/HasVisite_url", 'a') as f:
            for e in vlist:
                f.write(e + "\n")            
        #打印抓取但还未访问的链接
        with open(self.output + "/UnVisite_url", 'a') as f:
            for e in nlist:
                f.write(e + "\n")         





