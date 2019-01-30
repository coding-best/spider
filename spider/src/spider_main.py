#!/usr/bin/env python
# -*- coding:utf-8 -*-
##############################################
#
# main入口
#
############################################## 
import sys
import os
import time
import getopt
import logging
import log
import ConfigParser
import spider_crawl

def parse_opt(opts):
    """
    解析配置参数
    """
    try:
        opts, args = getopt.getopt(opts, 'c:h:v')
    except getopt.GetoptError as e:
        print '[ERROR] get opt failed: %s' % (e)
        print_help()
        sys.exit(-1)
    conf_file = ''

    for opt, value in opts:
        if opt == '-c':
            conf_file = value
        elif opt == '-v':
            print_version()
            sys.exit(0)
        elif opt == '-h':
            print_help()
            sys.exit(0)
        else:
            continue
    if conf_file == '':
        logging.error('[ERROR] get conf_file from opt failed')
        sys.exit(-1)
    return conf_file
            
    
def print_version():
    """
    打印版本信息
    """
    version = "1.0.0.0"
    print '%s' % (version)


def print_help():
    """
    打印帮助信息
    """
    print """
        main file:   ./spider_main.py 
        conf     :   /conf/spider.conf 
        Usage: python spider_main.py -c ./conf/spider.conf 
        """


def load_ini(conf_file):
    """
    通过conf文件加载配置
    """
    if not os.path.exists(conf_file):
        logging.error('Conf file: %s is not exist' % (conf_file))
        sys.exit(-1)
    try: 
        conf = {}
        ini_conf = ConfigParser.RawConfigParser()
        ini_conf.read(conf_file)
        if ini_conf != None :
            for each_string_option in [
                        'url_list_file',     #url种子文件
                        'output_directory',  #输出路径
                        'max_depth',         #最大深度
                        'crawl_interval',    #抓取间隔
                        'crawl_timeout',     #抓取超时时间
                        'target_url',        #目标url正则表达式
                        'thread_count']:     #线程数量
                if each_string_option in ini_conf.options('spider'):
                    conf[each_string_option] = ini_conf.get('spider', each_string_option)
                else:
                    raise ValueError('read conf: %s faild,please check your conf file' % each_string_option)
        return conf
    except Exception as e:
        logging.error("[ERROR] Read conf %s failed,INFO: %s" % (conf_file, e))
        return None            


if __name__ == "__main__":
    #初始化日志级别
    log.init_log(level=logging.INFO)
    #初始化conf配置
    if len(sys.argv[1:]) == 0:
        print_help()
        sys.exit(-1)       
    conf_file = parse_opt(sys.argv[1:])
    conf = load_ini(conf_file)
    if conf != None :
        spider = spider_crawl.Spider(conf)
        spider.run()
