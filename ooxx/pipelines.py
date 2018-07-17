# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import scrapy

class ooxxScrapyPipeline(ImagesPipeline):
    #通过修改file_path函数来改变图片保存的路径
    def file_path(self, request, response=None, info=None):
        #每套图的分类目录
        item = request.meta['item']
        #folder_name  = "full/%s.%s" % (item['folder_name'],item['image_url'].split('.')[-1])
        folder_name  = '%s/%s' % (item['folder_name'],item['img_name'])
        return folder_name

    def get_media_requests(self, item,info):
        for image_url in item['img_url']:
            yield scrapy.Request(image_url,meta={'item':item})

    def item_completed(self,results,item,info):
        #创建图片存储路径
        #列表生成式,将results的值分别给x,ok,如果ok的值为True,那么就取x['path']最后形成一个一个list
        #结果results为一个二元组的list，每个元组包含(success, image_info_or_error)
        #success: boolean值，success=true表示成功下载 ，反之失败
        #image_info_or_error 是一个包含下列关键字的字典（如果成功为 True ）或者出问题时为 Twisted Failure
        #字典包含以下键值对url：原始URL path：本地存储路径 checksum：校验码。失败则包含一些出错信息
        img_paths=[x['path'] for ok,x in results if ok]
        #判断图片是否下载成功，若不成功则抛出DropItem提示
        if not img_paths:
            raise DropItem('Item contains no images')
        return item
