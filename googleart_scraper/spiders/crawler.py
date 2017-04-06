# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from googleart_scraper.items import ArtworkItem


# TODO: on teh page of artist - get a painting url from a scroll list
# //*[@id="exp_tab_time"]/div/div/div/div[2]/div[1]/div/div[3]/content/div[1]/div[2]/a

class GoogleartCrawlSpider(CrawlSpider):
    name = 'artuk_crawler'
    allowed_domains = ['stackoverflow.com']
    start_urls = ['http://stackoverflow.com/questions?pagesize=50&sort=newest']

    rules = [
        Rule(LinkExtractor(allow=r'questions\?page=[0-9]&sort=newest'),
             callback='parse_item', follow=True)
    ]

    def parse(self, response):
        questions = response.xpath('//div[@class="summary"]/h3')

        for question in questions:
            item = ArtworkItem()
            item['url'] = question.xpath(
                'a[@class="question-hyperlink"]/@href').extract()[0]
            item['title'] = question.xpath(
                'a[@class="question-hyperlink"]/text()').extract()[0]
            yield item

    def parse(self, response):
        item = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        # 'https://lh5.ggpht.com/-HvgLbwqJ7Yy1iF9imtgsGhVDBDafmvTnDRZSCKl_PNjMT_KXaoNLuO4A7tb4Q'
        yield Request(item, self.parse_image)

    def parse_image(self, response):
        with open('image.jpg', 'w') as f:
            f.write(response.body)
