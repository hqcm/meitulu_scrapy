# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import random
import sys
import time

from scrapy import signals
from twisted.internet.error import (ConnectError, ConnectionRefusedError,
                                    TimeoutError)
from twisted.web._newclient import ResponseNeverReceived

#将模块的路径加到sys.path中
#'r'防止字符转义 如果路径中出现'\t'的话 不加r的话\t就会被转义 而加了'r'之后'\t'就能保留原有的样子
sys.path.append(r'C:\Users\Administrator\Desktop\scrapy1\ooxx')
import fetch_free_proxies

logger=logging.getLogger(__name__)

class ooxxSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ooxxDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None 

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        #对返回的response处理 
        #如果返回的response状态不是200，重新生成当前request对象  
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class HttpProxyMiddleware(object):
        #遇到这些类型的错误不再传给retry
        DONT_RETRY_ERRORS=(TimeoutError,ConnectionRefusedError,ResponseNeverReceived,ConnectError, ValueError)
        
        def __init__(self):
            #初始化代理列表
            #self.proxies=[{'proxy':None,'valid':True, 'count':0}] 此方法将自己搭建的可信代理和不使用代理加入初始代理列表
            #全部采用代理ip
            self.proxies=[]
            #将无法访问此网页的代理保存在无效代理列表中，而不是删除，这样可以避免在获取新的代理时将这些无效代理再次加入代理列表
            self.invalid_proxies=[]
            proxy_list=fetch_free_proxies.fetch_free_proxies()
            for proxy in proxy_list:
                self.proxies.append({'proxy':proxy})

        def process_request(self, request, spider):
            self.get_proxy(request)
            #固定格式：request.meta['proxy']=代理ip 

        def process_response(self, request, response, spider):
            # status不是正常的200而且不在spider声明的正常爬取过程中可能出现的
            #\表示代码换行
            if response.status != 200 \
                and (not hasattr(spider, 'website_possible_httpstatus_list') \
                or response.status not in spider.website_possible_httpstatus_list):
                self.invalid_proxies.append(self.proxies[0])  
                del self.proxies[0]
                #reqeust为什么要copy？
                new_request=request.copy()
                return new_request
            else:
                return response

        def process_exception(self,request,exception,spider):
            #处理使用代理时出现的异常
            if isinstance(exception, self.DONT_RETRY_ERRORS):
                new_request=request.copy()
                return new_request

        def get_proxy(self,request):
            if len(self.proxies)<2:
                self.fetch_new_proxies()
                proxy=self.proxies[0]
                if proxy['proxy']:
                    request.meta['proxy']=proxy['proxy']

        def fetch_new_proxies(self):
            #抓取新的代理添加到代理列表中
            count=0
            new_proxy_list=fetch_free_proxies.fetch_free_proxies()
            for new_proxy in new_proxy_list:
                if new_proxy not in (self.proxies or self.invalid_proxies):
                    self.proxies.append({'proxy':new_proxy})
            if  len(self.proxies)<2:
                logger.debug('暂停5分钟后再次抓取代理')
                time.sleep(300)
                count+=1
                #连续暂停两个五分钟后直接退出
                assert count==2
                self.fetch_new_proxies()
