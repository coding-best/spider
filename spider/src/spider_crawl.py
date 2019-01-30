#!/usr/bin/env python
# -*- coding:utf-8 -*-
##############################################
#
# 爬取程序 
#
############################################## 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../conf") 
import requests
import re
import threading
import Queue
import global_def
import logging
import log
import time
import os
import urlparse
import threading_pool
import random

urls_queue = Queue.Queue()
out_queue = Queue.Queue()
lock = threading.Lock()

has_visit_url = []
not_visit_url = []
#seeds = {'seed':'','current_depth':0}

class Spider():
    def __init__(self, conf):
        self.url_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.thread_stop = False
        self.pattern = str(conf['target_url'])
        self.max_depth = int(conf['max_depth'])
        self.output_dir = str(conf['output_directory'])
        self.thread_pool = threading_pool.ThreadPoolManger(int(conf['thread_count']))
        with open (conf['url_list_file']) as f:
            for line in f.readlines():
                url = line.strip('\r\n')
                if url != "":
                    seeds = {'seed':url, 'current_depth':0}
                    self.url_queue.put(seeds)

    def run(self):
        """
        main
        """
        while not self.url_queue.empty():
            seed = self.url_queue.get()
            self.thread_pool.add_job(self.spider, seed['seed'], seed['current_depth'])

        self.url_queue.join()
        print "craw done"
        print_result(self.output_dir,self.result_queue)


    def stop(self):
        """Stop push data thread.
        """
        self.thread_stop = True

    def spider(self, seed, current_depth):  
        print seed , "current_depth:%s\n" % current_depth
        next_depth = current_depth + 1
        html = get_html_content(seed)
        urlList =  get_url_from_html(html, self.pattern, seed)
        if urlList is None:
            print "urlList is None"
            return 0 

        for url in urlList:
            seed = {'seed':url, 'current_depth':next_depth}
            if next_depth  < self.max_depth:
                self.url_queue.put(seed)
                self.result_queue.put(seed)
            else:
                self.result_queue.put(seed)
        print "this seed craw done"
        self.url_queue.task_done()


def get_html_content(url, timeout=None, headers=None, type=None):
    """
    获取网页内容
    """
    if headers is None:
        headers = {}
    if timeout is None:
        timeout = 3
    try:
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url, headers=headers, verify=False, timeout=timeout) #, proxies=self.proxies, timeout=(3, 3))
        if response.status_code == 200:
            logging.info('get %s content successfully' % url)
            coding = response.apparent_encoding
            response.encoding = str(coding)
            return response.text
        else:
            logging.error("get url: %s faild,status_code = %s" % (url, response.status_code))     
    except Exception as e:
        logging.error("connect to the %s FAILD, %s" % (url, e.message)) 

def get_url_from_html(html, pattern, baseUrl):
    """
    获取网页内容里的url链接
    """
    #soup = BeautifulSoup(html, 'lxml')
    if html :
        url_list = re.findall(pattern, html, re.I)
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

def print_result(output_dir, queue):
    """
    输出结果
    """
    seed = []
    while not queue.empty():
        a = queue.get(timeout = 1)
        seed.append(a['seed'])
    with open (output_dir + "/crawed_url", 'a') as f:
        for e in seed:
            f.write(e + "\n")



"""test
"""
if __name__ == "__main__":

    log.init_log(level=logging.INFO)
    conf = {
        'url_list_file': '../conf/urls',
        'output_directory': './log',
        'target_url': '<a .*?href=\"([^javascript].*?)\".*?>', 
        'crawl_timeout': 3, 
        'crawl_interval': 1,
        'thread_count': 4,
        'max_depth': 1
        }

    a = Spider(conf)
    a.run()
    time.sleep(10)
    a.stop()
    print " main done"
    sys.exit(0)




