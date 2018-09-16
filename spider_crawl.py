#!/usr/bin/env python
# -*- coding:utf-8 -*-
##############################################
#
# 爬虫主模块
#
############################################## 

import sys
import requests
import re
import threading
import linkquence
import configuration as cf
import logging
import log
import time
import os
#import threading
#import BeautifulSoup



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
        for i in self.seeds:
            #mythread = MyThread(self.crawl(i))
            mythread = threading.Thread(target=self.crawl, args=(i,))
            self.threads.append(mythread)
        
        logging.info("Begin Crawling")
        for t in self.threads:
            logging.info("%s is start" % t.getName())
            t.start()

        for t in self.threads:
            t.join()
            logging.info("%s is done" % t.getName())
        sys.exit(0)

    def crawl(self, seed):
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
                urls = self.get_urls(html)
                if urls:
                    logging.info("get %s new links" % len(urls))
                    linksQuence.addVisitedUrl(visitUrl)
                    urlslink.extend(urls)
                    print urlslink
                else:
                    logging.error("get url:%s html error" % visitUrl)

            for url in urlslink:
                if url != "" and url not in linksQuence.getVisitedUrl():
                    linksQuence.addUnvisitedUrl(url)
            current_depth += 1
            urlslink = []                       
        logging.info("this thread crawling done!!! max_depth=%s" % self.max_depth)
        self.print_out(linksQuence)



    def get_html_content(self, url):

        try:
            requests.packages.urllib3.disable_warnings()
            response = requests.get(url, headers=self.headers, verify=False, timeout=(3,3)) #, proxies=self.proxies, timeout=(3, 3))
            if response.status_code == 200:
                logging.info('get %s content successfully' % url)
                coding = response.apparent_encoding
                response.encoding = str(coding)
                return response.text
            else:
                logging.error("get url: %s faild,status_code = %s" % (url, response.status_code))
        except Exception, e:
            logging.error("can not connect to the %s,info:%s" % (url, e.message) ) 

    def get_urls(self, html):
        #soup = BeautifulSoup(html, 'lxml')
        if html :
            urls = re.findall(self.pattern, html) 
            #转换为set去重
            real_urls = list(set(urls))
            return real_urls
        else:
            return None
    
    def print_out(self,linkquence):

        vlist = linkquence.getVisitedUrl()
        nlist = linkquence.getUnvisitedUrl()
        f = open(self.output, 'a')
        f.write(10*"-" + "has been visited urls:----------\n")
        for e in vlist:
            f.write(e + "\n")           
        f.write(10*"-" + "have not visited urls:----------\n")
        for e in nlist:
            f.write(e + "\n")
        f.close




