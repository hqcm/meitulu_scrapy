# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ooxxItem(scrapy.Item):
    folder_name = scrapy.Field()
    img_name = scrapy.Field()
    img_url = scrapy.Field()
   
