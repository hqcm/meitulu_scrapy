import re

import requests
import scrapy
from scrapy import Request

from ooxx.items import ooxxItem


class ooxx(scrapy.Spider):
    name='ooxx'
    allowed_domains=['meitulu.com']
    def start_requests(self):
        '爬取2到4页的图片'
        for i in range(2,4):
            url='https://www.meitulu.com/rihan/'+str(i)+'.html'
            yield Request(url=url, callback=self.parse1)

    def parse1(self,response):
        '获取每页日韩美女地址'
        urls = response.xpath('//ul[@class="img"]/li/a[1]/@href').extract()
        for url in urls:
                yield Request(url=url, callback=self.parse2)

    def parse2(self,response):
        '获取每页日韩美女对应的图片总页数'
        #总页数为倒数二项,且为只有一个元素的列表
        page_number=response.xpath('//center/div[@id="pages"]/a[last()-1]/text()').extract()[0]
        for i in range(int(page_number)):
            if i==0:
                url=response.url
            else:
                url=response.url.split('.html')[0]+'_'+str(i+1)+'.html'
            yield Request(url=url, callback=self.parse3)

    def parse3(self,response):
        '获取每页的图片'
        img_urls = re.findall(r'<img src="(.+?\.jpg)"', response.body.decode())
        image_url=[]
        for img_url in img_urls: 
            #挑出大图
            if img_url.split('/')[-2]==response.url.split('/')[-1].split('_')[0]:
                item=ooxxItem()
                #该网站美女名字格式不规范，仅以对应的数字作为文件夹的名字
                item['folder_name']=response.url.split('/')[-1].split('_')[0]
                item['img_name']=img_url.split('/')[-2]+'_'+img_url.split('/')[-1].split('_')[0]+'.jpg'
                image_url.append(img_url)
                item['img_url']=image_url
                yield item
