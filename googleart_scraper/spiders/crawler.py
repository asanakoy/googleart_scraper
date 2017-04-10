# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import Request

from googleart_scraper.items import ArtworkItem
from googleart_scraper.linkextractor import GoogleApiLinkExtractor


# TODO: on teh page of artist - get a painting url from a scroll list
# //*[@id="exp_tab_time"]/div/div/div/div[2]/div[1]/div/div[3]/content/div[1]/div[2]/a

class GoogleartCrawlSpider(CrawlSpider):
    name = 'artuk_crawler'
    # allowed_domains = ['https://www.google.com/']
    start_urls = ['https://www.google.com/culturalinstitute/beta/category/artist']

    rules = [
        Rule(GoogleApiLinkExtractor(base_url=u'https://www.google.com/culturalinstitute/beta/',
                                    allow=u'entity/.*\?categoryId\u003dartist'),
             callback='parse_artist', follow=True),
        Rule(GoogleApiLinkExtractor(base_url=u'https://www.google.com/culturalinstitute/beta/',
                                    allow=u'asset/.+/.+'),
             callback='parse_artwork', follow=False)
    ]

    # def parse(self, response):
    #     questions = response.xpath('//div[@class="summary"]/h3')
    #
    #     for question in questions:
    #         item = ArtworkItem()
    #         item['url'] = question.xpath(
    #             'a[@class="question-hyperlink"]/@href').extract()[0]
    #         item['title'] = question.xpath(
    #             'a[@class="question-hyperlink"]/text()').extract()[0]
    #         yield item

    def parse_artist(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
        # TODO:
        name = response.xpath('//*[@id="yDmH0d"]/div[3]/header/div[2]/h1/text()').extract()
        print 'Artist name:', name
        pass

    def parse_artwork(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
        # TODO:
        print 'Artwork page:', response.xpath('/html/head/title/@text')
        pass

    # def parse_page_wtih_img(self, response):
    #     item = response.xpath('//meta[@property="og:image"]/@content').extract_first()
    #     # 'https://lh5.ggpht.com/-HvgLbwqJ7Yy1iF9imtgsGhVDBDafmvTnDRZSCKl_PNjMT_KXaoNLuO4A7tb4Q'
    #     yield Request(item, self.parse_image)
    #
    # def parse_image(self, response):
    #     with open('image.jpg', 'w') as f:
    #         f.write(response.body)
