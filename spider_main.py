#!/usr/bin/env python
# -*- coding:utf-8 -*-
##############################################
#
# This is spider start module and read parameter
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
    """Parse start options
    Args:
        opts: the options input
    Returns:
        conf_file: return the config file of xagent
    """
    try:
        opts, args = getopt.getopt(opts, 'c:h:v')
    except getopt.GetoptError as e:
        print '[ERROR] getopt failed: %s' % (e)
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
    return conf_file
            
    
def print_version():
    """Print xagent version
    """
    version = "1.0.0.0"
    print '%s' % (version)
    return version


def print_help():
    """Print help info
    """
    print 'Usage: python spider_main.py -c ./spider.conf'

def load_ini(conf_file):
    """load init conf by file
    Args: 
        conf_file: ini conf parsed.
    Returns:
        config_object: if errors raised, return None
    """
    if not os.path.exists(conf_file):
        logging.error('Conf file: %s is not exist' % (conf_file))
        sys.exit(-1)
    try: 
        ini_conf = ConfigParser.RawConfigParser()
        ini_conf.read(conf_file)
        return ini_conf
    except Exception as e:
        logging.error("[ERROR] Read ini conf %s failed: %s" % (conf_file, e))
        return None            


if __name__ == "__main__":
    #初始化日志级别
    log.init_log(level=logging.INFO)
    #初始化conf配置
    conf = {}
    if len(sys.argv[1:])==0:
        print_help()
        sys.exit(-1)       
    conf_file = parse_opt(sys.argv[1:])
    ini_conf = load_ini(conf_file)
    if ini_conf != None :
        for each_string_option in ['url_list_file', 'output_directory', 'max_depth',\
         'crawl_interval', 'crawl_timeout', 'target_url', 'thread_count']:
            if each_string_option in ini_conf.options('spider'):
                conf[each_string_option] = ini_conf.get('spider', each_string_option)
            else:
                conf[each_string_option] = ''

    spider = spider_crawl.Spider(conf)
    spider.muti_thread_crawl()

