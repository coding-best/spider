#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# the spider function unitTest
# Authors: linyimin
# Date:    2018/9/29
##########################################################################

import unittest
import os
import mock
import sys
import commands
import ConfigParser

TEST_DIR = os.path.dirname(os.path.realpath(__file__)) 
TEST_CONF = TEST_DIR + "/test_file.conf"
MAIN_DIR = os.path.dirname(TEST_DIR)
sys.path.append('%s' % MAIN_DIR)
import spider_main
from spider_crawl import Spider
from linkquence import linkQuence

class mainTest(unittest.TestCase):
    """
    spider_main.py
    """
    def test_parse_opt(self):
        #假设输入参数
        parameter = ['-c', 'test_file.conf']
        conf_file = spider_main.parse_opt(parameter)
        self.assertEqual(conf_file, 'test_file.conf')

    def test_load_ini(self):
        #生成配置文件
        config = ConfigParser.ConfigParser()
        config.add_section("spider")
        config.set("spider", "name", "linyimin")
        config.set("spider", "age", "18")
        config.set("spider", "sex", "man")
        config.write(open(TEST_CONF,'w'))
        #读取配置文件内容
        conf = {}
        ini_conf = spider_main.load_ini(TEST_CONF)
        if ini_conf != None :
            for each_string_option in ['name', 'age', 'sex']:
                if each_string_option in ini_conf.options('spider'):
                    conf[each_string_option] = ini_conf.get('spider', each_string_option)
                else:
                    conf[each_string_option] = '' 
        os.remove(TEST_CONF)
        self.assertEqual(conf['name'], 'linyimin')
        self.assertEqual(conf['age'], '18')
        self.assertEqual(conf['sex'], 'man')       


    """
    spider_crawl.py
    """    
    def test_get_urls(self):
        visitUrl = "http://www.baidu.com"
        html = "<a href=\"http://write.blog.csdn.net\"></a> \
                <a href=\"/relatively_url\"> \
                </a> <a href=\"javascript\"></a> "
        target_urls = ['http://www.baidu.com/relatively_url', 'http://write.blog.csdn.net']
        #跳过init实例化类
        test_Spider= Spider.__new__(Spider)
        test_Spider.pattern="<a .*?href=\"([^javascript].*?)\".*?>"
        urls = test_Spider.get_urls(html,visitUrl)
        self.assertEqual(urls, target_urls)       


    """
    linkquence.py
    """
    def test_linkquence(self):
        links = linkQuence()
        links.addVisitedUrl('a')
        links.addVisitedUrl('b')
        links.addUnvisitedUrl('c')
        links.addUnvisitedUrl('d')
        links.removeVisitedUrl('b')
        #弹出未访问url为最先进队列的
        links.unVisitedUrlDeQuence()
        vi = links.getVisitedUrl()
        Unvi = links.getUnvisitedUrl()
        self.assertEqual(vi, ['a'])
        self.assertEqual(Unvi, ['d'])
        


if __name__ == '__main__':
    unittest.main()     